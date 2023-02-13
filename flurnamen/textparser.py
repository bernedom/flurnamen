'''text parser for markdown files'''


class textparser:
    def parse(self, filename):
        '''parse the text from a file'''
        with open(filename, 'r') as file:
            return file.read()
