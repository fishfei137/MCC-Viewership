import twitch_data
import yt_data
import error_alert
import logging
import now_bst
import mcc_website
import chatters
from timeit import default_timer as timer

now = now_bst.now()
game = mcc_website.get_game()
mcc_website.driver.quit()


def main():
    start = timer()
    try:
        yt_data.main(game)
    except:
        logging.exception(f"{now}")
        error_alert.tele_notify(remarks = '*Youtube: ERROR OCCURED*')
    end = timer()
    print(f"yt: {end-start}")

    start2 = timer()
    try:
        twitch_data.main(game)
    except:
        logging.exception(f"{now}")
        error_alert.tele_notify(remarks = '*Twitch: ERROR OCCURED*')
    end2 = timer()
    print(f"twitch: {end2-start2}")



if __name__ == "__main__":
    main()