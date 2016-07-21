import logging
import os
import platform
import shutil
from glob import glob

from libs import utils
from libs.Config import Config
from libs.Decorators.Asynchronous import asynchronous
from libs.Downloader import Downloader
from libs.PathsManager import PathsManager as pm


class UpdaterError(Exception):
    pass


class VersionInfo:
    def __init__(self, version, file_to_download_url="", libraries_names=list()):
        self.version = version
        """:type : str """
        self.file_to_download_url = file_to_download_url
        """:type : str | dict """
        self.libraries_names = libraries_names
        try:
            self.__get_version_numbers()
        except (ValueError, AttributeError):
            raise Exception("bad format version: {}".format(version))

    def __eq__(self, other):
        return self.version == other.version

    def __ne__(self, other):
        return self.version != other.version

    def __gt__(self, other):
        zipped = zip(self.__get_version_numbers(), other.__get_version_numbers())
        for s, o in zipped:
            if s > o:
                return True
            if s < o:
                return False
        return False

    def __ge__(self, other):
        return self > other or self == other

    def __le__(self, other):
        return other >= self

    def __lt__(self, other):
        return other > self

    def __get_version_numbers(self):
        return [int(n) for n in self.version.split(".")]

    def get_dictionary(self):
        return self.__dict__


class Web2BoardUpdater:
    __globalWeb2BoardUpdater = None
    log = logging.getLogger(__name__)

    def __init__(self):
        self.name = "Web2BoardUpdater"
        self.downloader = Downloader(refresh_time=1)

    def __extract_version_from_path(self, path):
        version_to_end = path.rsplit("_", 1)[1]
        return VersionInfo(version_to_end.rsplit(".", 1)[0])

    def get_new_downloaded_version(self):
        confirm_versions = glob(pm.get_dst_path_for_update("*.confirm"))
        versions = [self.__extract_version_from_path(v) for v in confirm_versions]
        if len(versions) == 0:
            return None
        greater_version = max(versions)
        return greater_version.version

    def clear_new_versions(self):
        confirm_versions = glob(pm.get_dst_path_for_update("*.confirm"))
        for confirm_version in confirm_versions:
            os.remove(confirm_version)
        zip_versions = glob(pm.get_dst_path_for_update("*.zip"))
        for zip_version in zip_versions:
            os.remove(zip_version)
        folder_versions = [f for f in glob(pm.get_dst_path_for_update("*")) if os.path.isdir(f)]
        for folder_version in folder_versions:
            shutil.rmtree(folder_version)

    def get_download_url(self, online_version_info):
        args = dict(arch=64 if utils.is64bits() else 32,
                    os=platform.system(),
                    version=online_version_info.version)

        return Config.download_url_template.format(**args)

    @asynchronous()
    def download_version(self, version, infoCallback=None):
        confirmationPath = pm.get_dst_path_for_update(version) + ".confirm"
        zipDstPath = pm.get_dst_path_for_update(version) + ".zip"
        if not os.path.exists(confirmationPath):
            url = self.get_download_url(VersionInfo(version))
            self.downloader.download(url, dst=zipDstPath, info_callback=infoCallback).result()
            utils.extract_zip(zipDstPath, pm.get_dst_path_for_update(version))
            os.remove(zipDstPath)
            with open(confirmationPath, "w"):
                pass

    @asynchronous()
    def update(self, version, destination):
        version_path = pm.get_dst_path_for_update(version)
        confirm_path = version_path + ".confirm"
        if not os.path.isdir(version_path) or not os.path.isfile(confirm_path):
            raise UpdaterError("Unable to update, not all necessary files downloaded")

        self.log.info("updating in process")
        utils.copytree(version_path, destination)

        if os.path.exists(destination):
            self.log.info("removing original files")
            utils.rmtree(destination)
            self.log.info("removed original files")
        else:
            os.makedirs(destination)
        utils.copytree(version_path, destination)
