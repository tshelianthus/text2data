import datetime
import os
import logging
from src.text2data import Text2DataApp


# 配置日志记录器
app_name = "text2data"
timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
process_id = os.getpid()
log_directory = "logs"
if not os.path.exists(log_directory):
    os.makedirs(log_directory)

log_filename = f"{log_directory}/{app_name}_{timestamp}_pid_{process_id}.log"

logging.basicConfig(
    level=logging.INFO,
    filename=log_filename,
    filemode="a",
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

if __name__ == "__main__":
    logging.info("程序执行")
    app = Text2DataApp()
    app.run()
