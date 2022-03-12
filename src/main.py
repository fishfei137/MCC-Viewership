import twitch_data
import yt_data
import error_alert
import logging
import now_bst
import mcc_website

now = now_bst.now()
game = mcc_website.get_game()
mcc_website.driver.quit()

try:
    yt_data.main(game)
except:
    logging.exception(f"{now}")
    error_alert.tele_notify(msg = '*ERROR OCCURED*', remarks = '*Youtube:*')

try:
    twitch_data.main(game)
except:
    logger = logging.getLogger(__name__)
    logger.exception(f"{now}")
    error_alert.tele_notify(msg = '*ERROR OCCURED*', remarks = '*Twitch:*')

