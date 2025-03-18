from loguru import logger
from helpers import *

TEST_TIMEOUT_SECONDS = os.environ.get("TESTING_TIMEOUT_SECONDS", 60)

@pytest.mark.timeout(TEST_TIMEOUT_SECONDS)
def test_dynatrace_ui(page: Page):

    # It is a classic app
    app_visual_name = "Settings Classic"
    app_name = "settings"

    ################################################
    logger.info("Logging in")
    login(page)

    # ################################################
    logger.info("Opening search menu")
    open_search_menu(page)
    
    
    # ################################################
    logger.info(f"Searching for {app_visual_name}")
    search_for(page, app_visual_name)

    # ################################################
    logger.info(f"Opening {app_visual_name} app")
    open_app_from_search_modal(page, app_name, is_classic_app=True)

    # ################################################
    logger.info(f"{app_name} app is now displayed")

    # Open tags menu
    logger.info("Opening Tags Menu")
    wait_for_app_to_load(page, is_classic_app=True)
    app_frame_locator, app_frame = get_app_frame_and_locator(page, is_classic_app=True)

    # Find and click on "Tags"
    expect(app_frame_locator.get_by_title("Tags", exact=True).first).to_contain_text("Tags", timeout=WAIT_TIMEOUT)
    tags_element = app_frame_locator.get_by_title("Tags", exact=True).first
    tags_element.click()

    # Find and click on "Automatically applied tags"
    automatically_applied_tags_element = app_frame_locator.get_by_title("Automatically applied tags", exact=True).first
    expect(automatically_applied_tags_element).to_contain_text("Automatically applied tags", timeout=WAIT_TIMEOUT)
    automatically_applied_tags_element.click()

    # Open invidual tag dropdown
    tag_name = "crossplane-created"

    # Expect tag NOT to exist
    expect(app_frame_locator.locator(f"dtx-markdown[uitestid=\"cell-summary\"] div.content:has-text(\"{tag_name}\")")).not_to_have_text(tag_name, timeout=WAIT_TIMEOUT)
