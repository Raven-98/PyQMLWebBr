# This Python file uses the following encoding: utf-8

from PySide2.QtCore import QFile, QTextStream

class Filters:
    _easyList = dict()

    def __init__(self):
        easyListFile = QFile("easylist.txt")
        if not easyListFile.open(QFile.ReadOnly):
            return
        self._easyList = {
                "blacklist": {
                        "base": [],
                        "baselist": [],
                        "domain": [],
                        "domainlist": [],
                        "basedomain": [],
                        "basedomainlist": [],
                        "domaindomain": [],
                        "domaindomainlist": []
                    },
                "whitelist": {
                        "base": [],
                        "baselist": [],
                        "domain": [],
                        "domainlist": [],
                        "basedomain": [],
                        "basedomainlist": [],
                        "domaindomain": [],
                        "domaindomainlist": []
                    }
            }
        inTextStream = QTextStream(easyListFile)
        inTextStream.readLine()
        while not inTextStream.atEnd():
            line = inTextStream.readLine();
            if line[0] != "!":
                if line.find("##") == -1 and line.find("#?#") == -1 and line.find("#@#") == -1 and line.find("#$#") == -1:
                    if line.find("$") == -1:
                        if not line.startswith("@@") and not line.startswith("##"):
                            if line.startswith("||") :
                                line = line[2:]
                                self._writeDict("blacklist", "domain", line)
                            else:
                                self._writeDict("blacklist", "base", line)
                        elif line.startswith("@@") and not line.startswith("##"):
                            line = line[2:]
                            if line.startswith("||") :
                                line = line[2:]
                                self._writeDict("whitelist", "domain", line)
                            else:
                                self._writeDict("whitelist", "base", line)
                    else:
                        list = line.split("$")
                        pattern_line = list[0]
                        arg_line = list[1]
                        if not self._chekSpecifyingFilterOptions(arg_line):
                            for item in arg_line.split(","):
                                if item.find("domain=") > -1:
                                    domain_list = item.replace("domain=", "").split("|")
                                    if self._checkInverseDomains(domain_list) != None:
                                        if not pattern_line.startswith("@@") and not pattern_line.startswith("##"):
                                            if pattern_line.startswith("||") :
                                                pattern_line = pattern_line[2:]
                                                if self._checkInverseDomains(domain_list):
                                                    for i in range(len(domain_list)):
                                                        domain_list[i] = domain_list[i][1:]
                                                    self._writeSuperDict("whitelist", "domaindomain", pattern_line, domain_list)
                                                else:
                                                    self._writeSuperDict("blacklist", "domaindomain", pattern_line, domain_list)
                                            else:
                                                if self._checkInverseDomains(domain_list):
                                                    for i in range(len(domain_list)):
                                                        domain_list[i] = domain_list[i][1:]
                                                    self._writeSuperDict("whitelist", "basedomain", pattern_line, domain_list)
                                                else:
                                                    self._writeSuperDict("blacklist", "basedomain", pattern_line, domain_list)
                                        elif pattern_line.startswith("@@") and not pattern_line.startswith("##"):
                                            pattern_line = pattern_line[2:]
                                            if pattern_line.startswith("||") :
                                                pattern_line = pattern_line[2:]
                                                if self._checkInverseDomains(domain_list):
                                                    for i in range(len(domain_list)):
                                                        domain_list[i] = domain_list[i][1:]
                                                    self._writeSuperDict("blacklist", "domaindomain", pattern_line, domain_list)
                                                else:
                                                    self._writeSuperDict("whitelist", "domaindomain", pattern_line, domain_list)
                                            else:
                                                if self._checkInverseDomains(domain_list):
                                                    for i in range(len(domain_list)):
                                                        domain_list[i] = domain_list[i][1:]
                                                    self._writeSuperDict("blacklist", "basedomain", pattern_line, domain_list)
                                                else:
                                                    self._writeSuperDict("whitelist", "basedomain", pattern_line, domain_list)


    def chekUrl(self, url):
        if len(self._easyList.keys()):
            if self._checkEasyListKey("whitelist", url):
                return False
            if self._checkEasyListKey("blacklist", url):
                return True
        return False

    def _checkEasyListKey(self, key, url):
        domainlist = self._easyList[key]["domainlist"]
        for list_item in domainlist:
            t = True
            for item in list_item:
                if url.find("http://%s" % item) == -1 or url.find("https://%s" % item) == -1:
                    t = False
                    break
            if t:
                return True

        domain = self._easyList[key]["domain"]
        for item in domain:
            if url.find("http://%s" % item) > -1 or url.find("https://%s" % item) > -1:
                return True

        baselist = self._easyList[key]["baselist"]
        for list_item in baselist:
            t = True
            for item in list_item:
                if url.find(item) == -1:
                    t = False
                    break
            if t:
                return True

        base = self._easyList[key]["base"]
        for item in base:
            if url.find(item) > -1:
                return True

        return False

    def _writeDict(self, key1, pattern_key2, line):
        if line.find("^") == -1 and line.find("\\") == -1:          # <= Якщо невиконується то перевірка через регулярні вирази
            self._writeDictNoReg(key1, pattern_key2, line)

    def _writeSuperDict(self, key1, pattern_key2, line, list):
        if line.find("^") == -1 and line.find("\\") == -1:
            self._writeSuperDictNoReg(key1, pattern_key2, line, list)

    def _writeDictNoReg(self, key1, pattern_key2, line):
        if line.find("*") == -1:
            self._easyList[key1]["%s" % pattern_key2].append(line)
        else:
            list = line.split("*")
            for item in list:
                if item == '':
                    list.remove(item)
            if len(list) > 1:
                self._easyList[key1]["%slist" % pattern_key2].append(list)
            else:
                self._easyList[key1]["%s" % pattern_key2].append(list[0])

    def _writeSuperDictNoReg(self, key1, pattern_key2, line, list):
        if line.find("*") == -1:
            self._easyList[key1]["%s" % pattern_key2].append({"pattern": line, "domain": list})
        else:
            pattern_list = line.split("*")
            for item in pattern_list:
                if item == '':
                    pattern_list.remove(item)
            if len(list) > 1:
                self._easyList[key1]["%slist" % pattern_key2].append({"pattern": pattern_list, "domain": list})
            else:
                self._easyList[key1]["%s" % pattern_key2].append({"pattern": pattern_list[0], "domain": list})

    def _chekSpecifyingFilterOptions(self, line):
        for item in self._specifyingFilterOptions:
            if line.find(item) > -1:
                return True
        return False

    def _checkInverseDomains(self, list):
        t = 0
        for item in list:
            if item.startswith("~"):
                t += 1
        if t == len(list):
            return True
        if t == 0:
            return False
        return None
