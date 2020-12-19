from transitions.extensions import GraphMachine

from utils import send_text_message, send_image_message


class TocMachine(GraphMachine):
    def __init__(self, **machine_configs):
        self.current_result=0
        self.machine = GraphMachine(model=self, **machine_configs)

    def is_going_to_menu(self, event):
        return True

    def is_going_to_summation(self, event):
        text = event.message.text
        return text.lower() == "1"

    def is_going_to_result(self, event):
        text = event.message.text
        if(text.lower().isnumeric()):
            return True
        else:
            return False

    def is_going_to_my_profile(self, event):
        text = event.message.text
        return text.lower() == "2"
    
    def is_going_to_show_fsm(self, event):
        text = event.message.text
        return text.lower() == "3"

    def on_enter_menu(self, event):
        print("I'm entering menu")

        reply_token = event.reply_token
        reply_string = "[menu]\nThis bot provides three functions\n1. summation\n2. my_profile\n3. show_fsm"
        send_text_message(reply_token, reply_string)

    def on_enter_summation(self, event):
        print("I'm entering summation")

        reply_token = event.reply_token
        reply_string = "[summation]\nEnter number to sum, if you reply non-digit number, you will be redirectted to state: menu"
        send_text_message(reply_token, reply_string)


    def on_enter_result(self, event):
        print("I'm entering result")

        reply_token = event.reply_token
        text = event.message.text
        self.current_result += int(text.lower())
        reply_string = "[result]\nsummation result now is " + str(self.current_result)
        send_text_message(reply_token, reply_string)
        self.go_back_to_summation()

    def on_enter_my_profile(self, event):
        print("I'm entering my_profile")

        reply_token = event.reply_token
        reply_string = "[my_profile]\n姓名：林禹丞\n系級：電機111\n學號：E24089070\n"
        reply_string += "\n-\n嗨嗨你好阿👋️\n-\n台北人，目前在台南唸書\n-\n"
        reply_string += "️平常喜歡吃沒吃過的餐廳（其實拉麵店🍜️居多哈哈）\n-\n喜歡聽爵士樂🎷️🎹️🎺️（非常喜歡Chet Baker)"
        reply_string += "️，也喜歡聽爵電影配樂🎥️（最喜歡新天堂樂園的)，平常也會聽一些獨立樂團（Cicada❤️)\n-"
        send_text_message(reply_token, reply_string)
        reply_string = "[menu]\nThis bot provides three functions\n1. summation\n2. my_profile"
        self.go_back(event)

    def on_enter_show_fsm(self, event):
        reply_token = event.reply_token
        url = "https://git.heroku.com/jeremyhillaryboob.git/show-fsm"
        send_image_message(reply_token, url)
        self.go_back(event)