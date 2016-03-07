#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'ipetrash'


import pickle
import shutil
import os
import traceback

from PySide.QtGui import *
from PySide.QtCore import *

from mainwindow_ui import Ui_MainWindow
from common import *


logger = get_logger('mainwindow')
DIR = 'tags'
DIR = 'tags3'


class MainWindow(QMainWindow, QObject):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.setWindowTitle('Preparation description tag stackoverflow')

        # Все действия к прикрепляемым окнам поместим в меню
        for dock in self.findChildren(QDockWidget):
            self.ui.menuDockWindow.addAction(dock.toggleViewAction())

        # Все действия к toolbar'ам окнам поместим в меню
        for tool in self.findChildren(QToolBar):
            self.ui.menuTools.addAction(tool.toggleViewAction())

        self.ui.action_save_tag.triggered.connect(self.save_tag)

        self.ui.ref_guide.textChanged.connect(self.ref_guide_text_changed)
        self.ui.description.textChanged.connect(self.description_text_changed)

        # TODO: при изменении тега менять и окно с его содержимым -- plain_text_edit_tag_info
        # TODO: заменить модель комбобокса нашим списком
        self.tags_dict = dict()
        self.modified_tags = set()

        # Словарь, ключом, которого id тега, а значением -- элемент списка
        self.tag_id_item_dict = dict()

        self.tag_list_model = QStandardItemModel()
        self.modified_tags_model = QStandardItemModel()

        self.ui.list_view_tag_list.setModel(self.tag_list_model)
        self.ui.list_view_modified_tags.setModel(self.modified_tags_model)

        # self.ui.tag_list.currentIndexChanged.connect(self.fill_tag_info_from_index)
        self.ui.list_view_tag_list.clicked.connect(self.list_view_tag_list_clicked)
        self.ui.list_view_modified_tags.clicked.connect(self.list_view_modified_tags_clicked)

        # TODO: добавить кнопку для постинга изменений тега. Перед постингом нужно авторизоваться
        # получить текущее состояние и сравнить с новым -- может кто-то что-то добавил и
        # если оно было лучше, того, что я хочу добавить, получится не хорошо

        # TODO: кнопка сохранения всех измененных тегов

        self.update_states()

    def update_states(self):
        self.ui.action_save_tag.setEnabled(False)

        index = self.ui.list_view_tag_list.currentIndex()
        tag_id = self.tag_id_from_index(index)
        if tag_id is not None:
            self.ui.action_save_tag.setEnabled(tag_id in self.modified_tags)

    def list_view_tag_list_clicked(self, index):
        item = self.tag_list_model.itemFromIndex(index)
        if item is not None:
            tag_id = item.data()
            self.fill_tag_info_from_id(tag_id)
        else:
            logger.warn('Item from index; "%s" not found.', index)

    def list_view_modified_tags_clicked(self, index):
        item = self.modified_tags_model.itemFromIndex(index)
        if item is not None:
            tag_id = item.data()
            tag_item = self.tag_id_item_dict[tag_id]
            self.ui.list_view_tag_list.setCurrentIndex(tag_item.index())

            self.fill_tag_info_from_id(tag_id)
        else:
            logger.warn('Item from index; "%s" not found.', index)

    @staticmethod
    def tag_title(tag):
        return '#{}: {}'.format(tag['id'], ', '.join(tag['name']))

    def fill_tag_list(self):
        self.tags_dict.clear()
        self.tag_list_model.clear()

        tag_file_list = [DIR + '/' + tag for tag in os.listdir(DIR) if tag.endswith('.tag')]
        for file_name in tag_file_list:
            with open(file_name, 'rb') as f:
                # Пример: {'ref_guide': '', 'id': '1', 'description': '', 'name': ['python']}
                data = pickle.load(f)
                data['hash'] = self.hash_tag(data)

                self.tags_dict[data['id']] = data

        self.ui.list_view_tag_list.blockSignals(True)

        logger.debug('Total tags: %s.', len(self.tags_dict))
        logger.debug('Fill list tags start.')

        # При долгой загрузкк показываем прогресс диалог
        progress = QProgressDialog("Adding tags...", "Abort", 0, len(self.tags_dict), self)
        progress.setWindowModality(Qt.WindowModal)
        progress.setWindowTitle('Progress dialog')

        tags = sorted(self.tags_dict.items(), key=lambda x: int(x[0]))
        for i, (tag_id, tag) in enumerate(tags):
            progress.setValue(i)
            if progress.wasCanceled():
                break

            name = self.tag_title(tag)

            item = QStandardItem(name)
            item.setData(tag_id)
            self.tag_list_model.appendRow(item)
            self.tag_id_item_dict[tag_id] = item

        progress.setValue(len(self.tags_dict))
        logger.debug('Fill list tags finish.')

        self.ui.list_view_tag_list.blockSignals(False)

        if self.tag_list_model.rowCount():
            item = self.tag_list_model.item(0)
            index = item.index()
            self.fill_tag_info_from_index(index)
            self.ui.list_view_tag_list.setCurrentIndex(index)

        self.update_states()

    def hash_tag(self, tag):
        text = tag['ref_guide'] + tag['description']

        import hashlib
        md5 = hashlib.md5()
        md5.update(text.encode())
        return md5.hexdigest()

    def check_modified_tag(self, tag_id):
        tag = self.tags_dict[tag_id]

        new_hash = self.hash_tag(tag)

        if tag['hash'] == new_hash:
            if tag_id in self.modified_tags:
                self.modified_tags.remove(tag_id)
        else:
            self.modified_tags.add(tag_id)

        # Если тег есть в списке измененных, меняем его цвет, иначе возвращаем черный цвет
        item = self.tag_id_item_dict[tag_id]
        item.setForeground(Qt.darkCyan if tag_id in self.modified_tags else Qt.black)

        font = item.font()
        font.setBold(tag_id in self.modified_tags)
        item.setFont(font)

        self.fill_list_modified_tags()

    def fill_list_modified_tags(self):
        # Обновление списка измененных тегов
        self.modified_tags_model.clear()

        for tag_id in sorted(self.modified_tags, key=int):
            tag = self.tags_dict[tag_id]
            item = QStandardItem(self.tag_title(tag))
            item.setData(tag_id)

            self.modified_tags_model.appendRow(item)

    def tag_id_from_index(self, index):
        if index.isValid():
            item = self.tag_list_model.itemFromIndex(index)
            if item is not None:
                return item.data()
            else:
                logger.warn('Item from index: "%s" is None.', index)
        else:
            logger.warn('Index: "%s" is not valid.', index)

    def ref_guide_text_changed(self):
        index = self.ui.list_view_tag_list.currentIndex()
        if not index.isValid():
            logger.warn('Index "%s" is not valid!', index)
            return

        tag_id = self.tag_id_from_index(index)
        tag = self.tags_dict[tag_id]
        tag['ref_guide'] = self.ui.ref_guide.toPlainText()

        self.check_modified_tag(tag_id)
        self.update_states()

    def description_text_changed(self):
        index = self.ui.list_view_tag_list.currentIndex()
        tag_id = self.tag_id_from_index(index)
        tag = self.tags_dict[tag_id]
        tag['description'] = self.ui.description.toPlainText()

        self.check_modified_tag(tag_id)
        self.update_states()

    def fill_tag_info_from_id(self, tag_id):
        if tag_id not in self.tags_dict:
            logger.warn('Tag id: "%s" not found!', tag_id)
            return

        tag = self.tags_dict[tag_id]
        logger.debug('Fill tag info from tag id: "%s", tag: %s', tag_id, tag)
        self.ui.plain_text_edit_tag_info.setPlainText(str(tag))

        url = 'http://ru.stackoverflow.com/tags/{}/info'.format(tag['name'][0])
        url = '<a href="{0}">{0}</a>'.format(url)
        self.ui.url.setText(url)

        self.ui.ref_guide.blockSignals(True)
        self.ui.description.blockSignals(True)

        self.ui.ref_guide.setPlainText(tag['ref_guide'])
        self.ui.description.setPlainText(tag['description'])

        self.ui.ref_guide.blockSignals(False)
        self.ui.description.blockSignals(False)

        self.update_states()

    def fill_tag_info_from_index(self, index):
        tag_id = self.tag_id_from_index(index)
        self.fill_tag_info_from_id(tag_id)

    def save_tag(self):
        index = self.ui.list_view_tag_list.currentIndex()
        tag_id = self.tag_id_from_index(index)
        tag = self.tags_dict[tag_id]

        file_name = DIR + '/{}.tag'.format(tag['id'])
        file_name_backup = file_name + '.backup'

        # Перед переписыванием файла, делаем его копию
        shutil.copyfile(file_name, file_name_backup)

        try:
            with open(file_name, mode='wb') as f:
                # Обновляем хеш
                tag['hash'] = self.hash_tag(tag)

                # Флаг, говорящий, что данный тег был изменен пользователем
                tag['user_changed'] = True

                self.modified_tags.remove(tag_id)
                self.fill_list_modified_tags()

                pickle.dump(tag, f)

        except Exception as e:
            logger.error('{}.\n\n{}'.format(e, traceback.format_exc()))
            logger.debug('Restore {} from {}.'.format(file_name, file_name_backup))

            # Произошла ошибка. Восстанавливаем файл из бекапа
            os.remove(file_name)
            os.rename(file_name_backup, file_name)
        else:
            logger.debug('Update {} was successful, removed the backup: {}.'.format(file_name, file_name_backup))

            # Переписывание прошло хорошо, удаляем файл бекапа
            if os.path.exists(file_name_backup):
                os.remove(file_name_backup)

        self.update_states()

    def read_settings(self):
        # TODO: при сложных настройках, лучше перейти на json или yaml
        config = QSettings(CONFIG_FILE, QSettings.IniFormat)
        self.restoreState(config.value('MainWindow_State'))
        self.restoreGeometry(config.value('MainWindow_Geometry'))
        self.ui.splitter.restoreState(config.value('Splitter_State'))

    def write_settings(self):
        config = QSettings(CONFIG_FILE, QSettings.IniFormat)
        config.setValue('MainWindow_State', self.saveState())
        config.setValue('MainWindow_Geometry', self.saveGeometry())
        config.setValue('Splitter_State', self.ui.splitter.saveState())

    def closeEvent(self, event):
        self.write_settings()
        quit()
