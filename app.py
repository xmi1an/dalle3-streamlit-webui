import os
import json
import datetime
import requests
from io import BytesIO
from PIL import Image
import streamlit as st
from openai import OpenAI

# Setting the page configuration
st.set_page_config(layout="wide", page_title="Avatar Generator", page_icon=":smiley:")


def load_config(config_path="config.json"):
    """Load configuration details from a JSON file."""
    try:
        with open(config_path) as f:
            return json.load(f)
    except FileNotFoundError:
        st.error("Configuration file not found.")
    except json.JSONDecodeError:
        st.error("Error decoding the configuration file.")
    return {}


def ensure_images_folder_exists(folder_name="images"):
    """Ensure the necessary directories are present."""
    os.makedirs(folder_name, exist_ok=True)


def find_default_index(data):
    """Find the index of the default value in the list."""
    try:
        return data.index("Default")
    except ValueError:
        # Return 0 if "Default" is not found
        return 0


def selectbox_with_default(column, label, options, key=None):
    """Create a selectbox in the specified column with a default value if present."""
    index = find_default_index(options)
    return column.selectbox(label, options, index=index, key=key)


def get_user_input(config):
    """Render user input controls and return the user inputs."""
    prompt = st.text_area(
        "Enter Prompt",
        value="A person who loves to read books.",
        help="Describe what kind of image you want.",
        key="prompt",
    )

    resolution_options = ["1024x1024", "1792x1024", "1024x1792"]
    resolution = st.radio(
        "Select Resolution",
        resolution_options,
        index=find_default_index(resolution_options),
        horizontal=True,
        key="resolution",
    )

    st.subheader("Basic Information")
    cols = st.columns(4)
    gender = selectbox_with_default(
        cols[0], "Gender", sorted(config.get("genders", [])), key="gender"
    )
    enable_gender = cols[0].checkbox("Enable", key="enable_gender")

    age = selectbox_with_default(cols[1], "Age", config.get("ages", []), key="age")
    enable_age = cols[1].checkbox("Enable", key="enable_age")

    cultural_background = selectbox_with_default(
        cols[2],
        "Cultural Background",
        sorted(config.get("cultural_backgrounds", [])),
        key="cultural_background",
    )
    enable_cultural_background = cols[2].checkbox(
        "Enable", key="enable_cultural_background"
    )

    artistic_style = selectbox_with_default(
        cols[3],
        "Artistic Style",
        sorted(config.get("artistic_styles", [])),
        key="artistic_style",
    )
    enable_artistic_style = cols[3].checkbox("Enable", key="enable_artistic_style")

    st.subheader("Design Preferences")
    cols = st.columns(4)
    personality_trait = selectbox_with_default(
        cols[0],
        "Personality Trait",
        sorted(config.get("personality_traits", [])),
        key="personality_trait",
    )
    enable_personality_trait = cols[0].checkbox(
        "Enable", key="enable_personality_trait"
    )

    accessories = cols[1].multiselect(
        "Accessories", sorted(config.get("accessories", [])), key="accessories"
    )
    enable_accessories = cols[1].checkbox("Enable", key="enable_accessories")

    clothing_style = selectbox_with_default(
        cols[2],
        "Clothing Style",
        sorted(config.get("clothing_styles", [])),
        key="clothing_style",
    )
    enable_clothing_style = cols[2].checkbox("Enable", key="enable_clothing_style")

    hair_style_color = selectbox_with_default(
        cols[3],
        "Hair Style/Color",
        sorted(config.get("hair_styles_colors", [])),
        key="hair_style_color",
    )
    enable_hair_style_color = cols[3].checkbox("Enable", key="enable_hair_style_color")

    st.subheader("Appearance")
    cols = st.columns(4)
    expression = selectbox_with_default(
        cols[0], "Expression", sorted(config.get("expressions", [])), key="expression"
    )
    enable_expression = cols[0].checkbox("Enable", key="enable_expression")

    eye_color = selectbox_with_default(
        cols[1], "Eye Color", sorted(config.get("eye_colors", [])), key="eye_color"
    )
    enable_eye_color = cols[1].checkbox("Enable", key="enable_eye_color")

    skin_tone = selectbox_with_default(
        cols[2], "Skin Tone", sorted(config.get("skin_tones", [])), key="skin_tone"
    )
    enable_skin_tone = cols[2].checkbox("Enable", key="enable_skin_tone")

    body_type = selectbox_with_default(
        cols[3], "Body Type", sorted(config.get("body_types", [])), key="body_type"
    )
    enable_body_type = cols[3].checkbox("Enable", key="enable_body_type")

    pose = selectbox_with_default(
        cols[0], "Pose", sorted(config.get("poses", [])), key="pose"
    )
    enable_pose = cols[0].checkbox("Enable", key="enable_pose")

    background = selectbox_with_default(
        cols[1], "Background", sorted(config.get("backgrounds", [])), key="background"
    )
    enable_background = cols[1].checkbox("Enable", key="enable_background")

    return {
        "prompt": prompt.strip(),
        "resolution": resolution,
        "gender": gender,
        "age": age,
        "cultural_background": cultural_background,
        "artistic_style": artistic_style,
        "pose": pose,
        "background": background,
        "personality_trait": personality_trait,
        "accessories": accessories,
        "clothing_style": clothing_style,
        "hair_style_color": hair_style_color,
        "expression": expression,
        "eye_color": eye_color,
        "skin_tone": skin_tone,
        "body_type": body_type,
        "enable_gender": enable_gender,
        "enable_pose": enable_pose,
        "enable_background": enable_background,
        "enable_age": enable_age,
        "enable_cultural_background": enable_cultural_background,
        "enable_artistic_style": enable_artistic_style,
        "enable_personality_trait": enable_personality_trait,
        "enable_accessories": enable_accessories,
        "enable_clothing_style": enable_clothing_style,
        "enable_hair_style_color": enable_hair_style_color,
        "enable_expression": enable_expression,
        "enable_eye_color": enable_eye_color,
        "enable_skin_tone": enable_skin_tone,
        "enable_body_type": enable_body_type,
    }


def generate_avatar(client, config, folder_name="images"):
    """Generate the avatar image using the OpenAI API."""
    prompt = config["prompt"]
    if not prompt:
        st.error("Prompt cannot be empty.")
        return

    attributes = []
    if config["enable_gender"]:
        attributes.append(f"- Gender: {config['gender']}")
    if config["enable_pose"]:
        attributes.append(f"- Pose: {config['pose']}")
    if config["enable_background"]:
        attributes.append(f"- Background: {config['background']}")
    if config["enable_age"]:
        attributes.append(f"- Age: {config['age']}")
    if config["enable_cultural_background"]:
        attributes.append(f"- Cultural background: {config['cultural_background']}")
    if config["enable_artistic_style"]:
        attributes.append(f"- Artistic style: {config['artistic_style']}")
    if config["enable_personality_trait"]:
        attributes.append(f"- Personality trait: {config['personality_trait']}")
    if config["enable_accessories"]:
        accessories = (
            ", ".join(config["accessories"]) if config["accessories"] else "None"
        )
        attributes.append(f"- Accessories: {accessories}")
    if config["enable_clothing_style"]:
        attributes.append(f"- Clothing style: {config['clothing_style']}")
    if config["enable_hair_style_color"]:
        attributes.append(f"- Hair style/color: {config['hair_style_color']}")
    if config["enable_expression"]:
        attributes.append(f"- Expression: {config['expression']}")
    if config["enable_eye_color"]:
        attributes.append(f"- Eye color: {config['eye_color']}")
    if config["enable_skin_tone"]:
        attributes.append(f"- Skin tone: {config['skin_tone']}")
    if config["enable_body_type"]:
        attributes.append(f"- Body type: {config['body_type']}")

    if attributes:
        full_prompt = (
            f"Image of {prompt}.\n\nWith the following attributes:\n"
            + "\n".join(attributes)
            + "\n\nAvoids using explicit labels or pointers to indicate the requested attributes."
        )
    else:
        full_prompt = prompt

    st.caption(f"Full Prompt: `{full_prompt}`")

    try:
        with st.spinner("⌛ Generating the image..."):
            response = client.images.generate(
                model="dall-e-3",
                prompt=full_prompt,
                n=1,
                size=config["resolution"],
                quality="hd",
            )
        st.balloons()
        image_url = response.data[0].url
        revised_prompt = response.data[0].revised_prompt
        st.caption(f"[Image URL]({image_url})")
        st.markdown(f"Revised Prompt: `{revised_prompt}`")

        # Fetch and display the image
        with st.spinner("🖼️ Loading the image..."):
            image_response = requests.get(image_url)
            image = Image.open(BytesIO(image_response.content))
            st.image(image, caption="Generated Image")

        # Save the image to the images folder
        timestamp = datetime.datetime.now().isoformat().replace(":", "_")
        image_path = os.path.join(folder_name, f"avatar_{timestamp}.jpg")
        image.save(image_path)

        # Store the image and path in session state
        st.session_state["image"] = BytesIO(image_response.content)
        st.session_state["image_format"] = image.format
        st.session_state["image_path"] = image_path

    except Exception as e:
        st.error(f"Error: {e}")
        st.snow()


def main():
    """Entry point for the Streamlit app."""
    st.sidebar.title("Enter your OpenAI API key")
    api_key = st.sidebar.text_input("OpenAI API Key", type="password")

    if api_key:
        config = load_config()
        if config:
            client = OpenAI(api_key=api_key)
            ensure_images_folder_exists()
            user_input = get_user_input(config)

            if "generate_button_clicked" not in st.session_state:
                st.session_state["generate_button_clicked"] = False

            if not st.session_state["generate_button_clicked"]:
                if st.button("Generate Image 🪄"):
                    st.session_state["generate_button_clicked"] = True
                    generate_avatar(client, user_input)

            if st.session_state.get("image"):
                st.download_button(
                    label="📥 Download Image",
                    data=st.session_state.get("image"),
                    file_name=f"avatar.{st.session_state.get('image_format', 'jpg').lower()}",
                    mime=f"image/{st.session_state.get('image_format', 'jpeg').lower()}",
                )

            if st.session_state.get("image_path"):
                st.success(f"Image saved to: {st.session_state['image_path']}")
                st.session_state["generate_button_clicked"] = False

    else:
        st.sidebar.error("OpenAI API Key is required to generate avatars.")


if __name__ == "__main__":
    main()
