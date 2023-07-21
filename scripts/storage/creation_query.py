query = '''
drop table if exists users;
drop table if exists books;
drop table if exists lexicon;
drop table if exists menu_commands;

CREATE TABLE IF NOT EXISTS public.books
(
    id serial PRIMARY KEY,
    name text,
    content jsonb
);

CREATE TABLE IF NOT EXISTS public.lexicon
(
    key character varying,
    value text
);

CREATE TABLE IF NOT EXISTS public.menu_commands
(
    command character varying,
    description text
);

CREATE TABLE IF NOT EXISTS public.users
(
    user_id integer PRIMARY KEY,
    current_book integer,
    current_page integer,
    books integer[],
    book_marks jsonb,
	CONSTRAINT fkkey_users_current_book FOREIGN KEY (current_book) REFERENCES public.books (id)
);


INSERT INTO lexicon (key, value)
VALUES
    ('/start', 'Привет, читатель!\n\nЭто бот с помощью которого ты можешь добавлять книги в свою библиотеку, для удобного чтения\n\nЧтобы посмотреть список доступных команд - набери /help'),
    ('/help', 'Доступные команды:\n\n/continue - продолжить чтение\n/books - список ваших книг\n/bookmarks - посмотреть список закладок у текущей книги\n/help - справка по работе бота\n\nЧтобы добавить книгу, отправьте её в виде текстового файла в любой момент нашего общения, если требуется задать имя отличное от имени файла, отправьте его в поле под файлом\n\nЧтобы сохранить закладку - нажмите на кнопку с номером страницы\n\nПриятного чтения!'),
    ('/books', 'Это список ваших книг:'),
    ('/bookmarks', 'Это список ваших закладок:'),
    ('cant_parse', 'Я не смог спарсить данный файл :(\nПроверьте его исправность'),
    ('forward', '>'),
    ('backward', '<'),
    ('edit_books', 'Редактировать книги:'),
    ('no_books', 'В вашей библиотеке нет книг, чтобы добавить книгу, отправьте её в виде текстового файла'),
    ('no_books_to_delete', 'Не осталось книг для редактирования'),
    ('book_exists', 'Книга с таким именем уже существует, попробуйте переименовать файл'),
    ('deleted_book', 'Книга успешно удалена'),
    ('edit_bookmarks', 'Редактировать закладки:'),
    ('no_bookmarks', 'У вас пока нет ни одной закладки.\n\nЧтобы добавить страницу в закладки - во время чтения книги нажмите на кнопку с номером этой страницы\n\n/continue - продолжить чтение'),
    ('edit_button', 'РЕДАКТИРОВАТЬ'),
    ('edit', 'Вы перешли в режим редактирования'),
    ('del', '❌'),
    ('cancel', 'ОТМЕНИТЬ'),
    ('cancel_text', '/continue - продолжить чтение'),
    ('miss_message', 'Данное сообщение не предусмотрено моей логикой, посмотрите справку по использованию - /help');

INSERT INTO menu_commands (command, description)
VALUES
    ('/continue', 'Продолжить чтение'),
    ('/books', 'Мои книги'),
    ('/bookmarks', 'Мои закладки'),
    ('/help', 'Справка по работе бота');
'''
