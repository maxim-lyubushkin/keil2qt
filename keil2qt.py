import xml.etree.ElementTree as ET
import os


def get_base_qt_template():
    content = '''QT += core
QT -= gui\n
CONFIG += c++11\n
TARGET = qt
CONFIG += console
CONFIG -= app_bundle\n
TEMPLATE = app\n\n
DEFINES += QT_DEPRECATED_WARNINGS\n
'''
    return content


def get_target_name(root):
    tag = 'TargetName'
    name = ''
    for child_of_root in root.iter(tag):
        name = child_of_root.text

    if len(name) == 0:
        raise IOError('Empty target name')

    return name


def get_include_path_list(root):
    section = 'VariousControls'
    tag = 'IncludePath'
    includes = []

    # Разобрать секцию с заголовочными файлами
    for child_of_root in root.iter(section):
        for child_of_section in child_of_root.iter(tag):
            if child_of_section.text is not None:
                includes.append(child_of_section.text)

    # Разобрать секцию с исходниками
    section = 'File'
    tag = 'FilePath'
    for child_of_root in root.iter(section):
        for child_of_section in child_of_root.iter(tag):
            source_file = child_of_section.text
            source_file = source_file.replace('\\', '/')  # могут быть обратные слеши
            source_path = source_file[:source_file.rfind('/')]  # удаляем имя файла, оставляя только путь

            # пропустить startup - файл
            if source_file.find('startup') == 0:
                continue

            if source_path not in includes:
                includes.append(source_path)

    return include_path_to_str_list(includes)


def include_path_to_str_list(raw_includes):
    includes_str_list = []
    delimiter = ';'
    for element in raw_includes:
        for path in element.split(delimiter):
            # преобразуем слеши к единому формату
            formatted_path = path.replace('\\', '/')

            # добавим в списсок, чтобы небыло дублирований
            if formatted_path not in includes_str_list:
                includes_str_list.append(formatted_path)

    return includes_str_list


def get_include_path_section(root):
    includes = get_include_path_list(root)
    delimiter = '  \\\n'
    tab_padding = '\t'
    content = 'INCLUDEPATH += ' + delimiter
    for path in includes:
        content += tab_padding + path + delimiter

    return content


def get_define_section(root):
    defines = get_define_list(root)
    delimiter = '  \\\n'
    content = 'DEFINES += ' + delimiter
    for element in defines:
        content += element + delimiter

    return content


def get_define_list(root):
    section = 'VariousControls'
    tag = 'Define'
    defines = []

    for child_of_root in root.iter(section):
        for child_of_section in child_of_root.iter(tag):
            if child_of_section.text is not None:
                defines.append(child_of_section.text)

    return defines_to_str_list(defines)


def defines_to_str_list(raw_defines):
    defines_str_list = []
    delimiter = ','
    for element in raw_defines:
        defines_str_list.extend(element.split(delimiter))

    return defines_str_list


def get_files_list(includes):
    headers = []
    sources = []

    def remove_prefix(text, prefix):
        if text.startswith(prefix):
            return text[len(prefix):]

    for dir in includes:
        for file in os.listdir(dir):
            # file_dir = remove_prefix(dir, '../')

            if file.endswith(".h") or file.endswith(".hpp"):
                headers.append(dir + '/' + file)
            elif file.endswith(".c") or file.endswith(".cpp"):
                sources.append(dir + '/' + file)

    return headers, sources


def get_files_section(root):
    includes = get_include_path_list(root)
    delimiter = '  \\\n'
    tab_padding = '\t'
    headers, sources = get_files_list(includes)

    header_content = 'HEADERS += ' + delimiter
    for file in headers:
        header_content += tab_padding + file + delimiter

    source_content = 'SOURCES += ' + delimiter
    for file in sources:
        source_content += tab_padding + file + delimiter

    return header_content + '\n\n' + source_content


def make_pro_file(root):
    section_delimiter = '\n'
    content = get_base_qt_template() + section_delimiter
    content += get_define_section(root) + section_delimiter
    content += get_include_path_section(root) + section_delimiter
    content += get_files_section(root)
    return content


def find_keil_project_file():
    target_format = '.uvprojx'
    for file in os.listdir():
        if file.endswith(target_format):
            return file

    print("Keil project file not found")
    return None


def save_qt_project_file(content, filename):
    extension = '.pro'
    file = open(filename + extension, 'w')
    file.write(content)
    file.close()


if __name__ == '__main__':
    keil_pro_file = find_keil_project_file()
    if keil_pro_file is not None:
        tree = ET.parse(keil_pro_file)
        root = tree.getroot()
        qt_project_content = make_pro_file(root)
        print(qt_project_content)
        save_qt_project_file(qt_project_content, get_target_name(root))

    os.system("pause")
