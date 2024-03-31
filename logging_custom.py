import datetime


class LoggingCustom():
  def __init__(self, name) -> None:
    self.name = name

  def getDateTimeFormat(self):
    return datetime.datetime.now()

  def warning(self, message):
    print(f'{self.getDateTimeFormat()} {self.name}: WARNING {message}')
