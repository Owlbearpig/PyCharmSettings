import update_all_members_db_table
import datetime
import time
import character_groups

if __name__ == '__main__':

    print_update = datetime.timedelta(minutes=30)
    while True:
        update_all_members_db_table.update_main()
        character_groups.create_member_links()
        ctr = 12
        while ctr != 0:
            print("time until next update {}".format(ctr * print_update))
            ctr -= 1
            time.sleep(30 * 60)