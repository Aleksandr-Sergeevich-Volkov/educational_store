class Human:
    def __init__(self, name):
        self.name = name

    # ответ по умолчанию для всех одинаковый, можно 
    # доверить его родительскому классу
    def answer_question(self, question='Очень интересный вопрос! Не знаю.'):
        return print(question)


class Student(Human):
    def __init__(self, name):
        super().__init__(name)
    #  метод ask_question() принимает параметр someone:
    #  это объект, экземпляр класса Curator, Mentor или CodeReviewer,
    #  которому Student задаёт вопрос; 
    #  параметр question — это просто строка
    #  имя объекта и текст вопроса задаются при вызове метода ask_question
    def ask_question(self, someone, question):
        # напечатайте на экран вопрос в нужном формате
        print(f'{someone}, {question}')
        # запросите ответ на вопрос у someone
        print()  # этот print выводит разделительную пустую строку	


class Curator(Human):
    def __init__(self, name):
        super().__init__(name)      

    def __str__(self):
        return self.name      
    
    def answer_question(self, question):
        # здесь нужно проверить, пришёл куратору знакомый вопрос или нет
        # если да - ответить на него
        # если нет - вызвать метод answer_question() у родительского класса
        #if super().answer_question(question)=='Марина мне грустненько, что делать?':
        #print('Держись, всё получится. Хочешь видео с котиками?')
        #return super().answer_question()    
        return super().answer_question(question)    
    #super().answer_question('Держись, всё получится. Хочешь видео с котиками?') 
   

# объявите и реализуйте классы CodeReviewer и Mentor
class CodeReviewer(Human):
    def __init__(self, name):
        super().__init__(name)
    def __str__(self):
        return self.name 
    def answer_question(self, question):
        # здесь нужно проверить, пришёл куратору знакомый вопрос или нет
        # если да - ответить на него
        # если нет - вызвать метод answer_question() у родительского класса
        if question=='Евгений, что не так с моим проектом?':
            print('О, вопрос про проект, это я люблю.')
        return super().answer_question()    

class Mentor(Human):
    def __init__(self, name):
        super().__init__(name)
    def __str__(self):
        return self.name 
    def answer_question(self, question):
        # здесь нужно проверить, пришёл куратору знакомый вопрос или нет
        # если да - ответить на него
        # если нет - вызвать метод answer_question() у родительского класса
        if question=='Ира, как устроиться работать питонистом?':
            print('Сейчас расскажу')
        elif question=='Ира, мне грустненько, что делать?':
            print('Отдохни и возвращайся с вопросами по теории.')    
        else:
            return super().answer_question()    

# следующий код менять не нужно, он работает, мы проверяли
student1 = Student('Тимофей')
curator = Curator('Марина')
#mentor = Mentor('Ира')
#reviewer = CodeReviewer('Евгений')
#friend = Human('Виталя')

student1.ask_question(curator, 'мне грустненько, что делать?')
#student1.ask_question(mentor, 'мне грустненько, что делать?')
#student1.ask_question(reviewer, 'когда каникулы?')
#student1.ask_question(reviewer, 'что не так с моим проектом?')
#student1.ask_question(friend, 'как устроиться на работу питонистом?')
#student1.ask_question(mentor, 'как устроиться работать питонистом?')
curator.answer_question('Держись, всё получится. Хочешь видео с котиками?')