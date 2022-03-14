import twitch_data
import yt_data
import error_alert
import logging
import now_bst
import mcc_website

now = now_bst.now()
game = mcc_website.get_game()
mcc_website.driver.quit()


def main():

    try:
        yt_data.main(game)
    except:
        logging.exception(f"{now}")
        error_alert.tele_notify(remarks = '*Youtube: ERROR OCCURED*')

    try:
        twitch_data.main(game)
    except:
        logging.exception(f"{now}")
        error_alert.tele_notify(remarks = '*Twitch: ERROR OCCURED*')



if __name__ == "__main__":
    main()