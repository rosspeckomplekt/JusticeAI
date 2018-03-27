from feature_extraction.post_processing.regex.regex_lib import RegexLib
import re
import datetime
import time
import unicodedata
from util.log import Log


class EntityExtraction:
    regex_bin = None
    one_day = 86400  # unix time for 1 day
    month_dict = {
        'janvier': 1,
        'fevrier': 2,
        'mars': 3,
        'avril': 4,
        'mai': 5,
        'juin': 6,
        'juillet': 7,
        'aout': 8,
        'septembre': 9,
        "octobre": 10,
        'novembre': 11,
        'decembre': 12
    }

    def __init__(self):
        pass

    @staticmethod
    def match_any_regex(text, regex_array, regex_type):
        """
        1) Loads the regex binaries only once. If it is loaded then continue.
        2) Iterate all the regex and search text
        3) if regex finds a match then extract entity from this sub sentence

        :param text: String representation of precedent
        :param regex_array: List of regex
        :param regex_type: Entity we look for in a particular regex match
        :return: (Boolean, entity<int>)
        """
        if EntityExtraction.regex_bin is None:
            EntityExtraction.regex_bin = RegexLib.model
        for regex in regex_array:
            regex_result = regex.search(text)
            if regex_result:
                sentence = regex_result.group(0).lower()
                return EntityExtraction.__extract_regex_entity(sentence, regex_type)
        return False, 0

    @staticmethod
    def __extract_regex_entity(sentence, regex_type):
        """
        Entity extraction from the text

        1) If the type is BOOLEAN then simply return True, 1
        2) If the type is MONEY_REGEX then extract the money value and format string so that it is
           convertible to integer
        3) else return False, 1

        :param sentence: sub sentence from text to apply regex
        :param regex_type: type of information to extract
        :return: (boolean, int)
        """

        # removes accents
        nfkd_form = unicodedata.normalize('NFKD', sentence)
        sentence = u"".join([character for character in nfkd_form if not unicodedata.combining(character)])

        if regex_type == 'BOOLEAN':
            return True, 1

        elif regex_type == 'MONEY_REGEX':
            return EntityExtraction.__regex_money(regex_type, sentence)

        elif regex_type == 'DATE_REGEX':
            return EntityExtraction.__regex_date('DURATION_REGEX', sentence)
        return False, 0

    @staticmethod
    def __regex_date(sentence):
        """
        Tries to find date range within a sentence by trying to match against to regexes.
        First regex looks for the following format: 1er decembre 20** [a|au|et ...] 30 mai 20**
        Second regex looks for 2 or more months being stated
        convert to unix. ** We don't care about the year
            1) unless specified, start date is assumes to be the first day of the month
            2) unless specified, end date is assume to be the last day of the month. 28 is chosen because
                 every month have at least 28 days
        The information captured be the regexes above allows us to get the time difference in days

        :param sentence: sentence to extract entities
        :return: boolean (date found), integer (days between dates)
        """

        start_end_date_regex = re.compile(r"(?i)(\d{1,2})?(?:er|èr|ere|em|eme|ème)?\s?(\w{3,9}) (\d{4}) (?:a|à|au|et|"
                                          r"et se terminant le) (\d{1,2})?(?:er|èr|ere|em|eme|ème)?\s?(\w{3,9}) (\d{4})"
                                          , re.IGNORECASE)
        entities = re.findall(start_end_date_regex, sentence)

        if entities.__len__() > 0:
            entities = re.findall(start_end_date_regex, sentence).pop(0)

            try:
                start_day = int(entities[0])
            except ValueError as error:
                Log.write(str(error) + ": could not convert " + entities[0] + " to an int")
                start_day = '1'

            start_month = ''
            try:
                start_month = str(EntityExtraction.month_dict[entities[1]])
            except IndexError as error:
                Log.write(str(error) + ":" + str(start_month) + " is not a month or has spelling mistake")
                return False, 0

            start_year = entities[2]

            try:
                end_day = int(entities[3])
            except ValueError as error:
                Log.write(str(error) + ": could not convert " + entities[3] + " to an int")
                end_day = '28'

            try:
                end_month = str(EntityExtraction.month_dict[entities[4]])
            except IndexError as error:
                Log.write(str(error) + ":" + str(start_month) + " is not a month or has spelling mistake")
                return False, 0

            end_year = entities[5]

            start_unix = EntityExtraction.__date_to_unix([start_day, start_month, start_year])
            end_unix = EntityExtraction.__date_to_unix([end_day, end_month, end_year])

            return True, EntityExtraction.__get_time_interval_in_days(start_unix, end_unix)

        months_regex = re.compile(
            r"(janvier|fevrier|mars|d'avril|avril|mai|juin|juillet|d'aout|aout|septembre|d'octobre|octobre|novembre|decembre)",
            re.IGNORECASE)

        entities = re.findall(months_regex, sentence)
        if entities.__len__() > 1:
            total_months = entities.__len__()
            start_unix = EntityExtraction.__date_to_unix(['1', '1', '1970'])
            end_unix = EntityExtraction.__date_to_unix(['28', str(total_months), '1970'])
            return True, EntityExtraction.__get_time_interval_in_days(start_unix, end_unix)

        return False, 0

    @staticmethod
    def __regex_money(regex_type, sentence):
        """

        1) create the date regex --> re.compile(regex string)
        2) Find the dollar amount in the sentence
        3) filter the string by removing unecessary characters
        4) return the entity

        :param regex_type: str(MONEY_REGEX)
        :param sentence: boolean, integer
        :return:
        """
        generic_regex = re.compile(EntityExtraction.regex_bin[regex_type])
        entity = generic_regex.search(sentence).group(0)

        # Functional but not sure about how optimal it is
        entity = entity.replace("$", "")
        entity = entity.replace(" ", "")
        entity = entity.replace(",", ".")
        if entity[-1] == '.':
            entity = entity[:-1]
        return True, entity

    @staticmethod
    def __date_to_unix(date):
        """
        Given a date list (ex: [30,12,2019]) this function gets the unix time that represents this date
        :param date: date to convert into unix time
        :return: unix time representing the input date
        """
        date_string = " ".join(date)
        try:
            unix_time = time.mktime(datetime.datetime.strptime(date_string, '%d %m %Y').timetuple())
        except (ValueError, OverflowError) as error:
            Log.write(str(error) + ": " + str(date_string))
            return None

        return unix_time

    @staticmethod
    def __get_time_interval_in_days(first_date, second_date):
        """
        Calculates the time difference between 2 dates
        :param first_date: date in unix time
        :param second_date: date in unix time
        :return: time difference between 2 dates
        """
        return int(abs(first_date - second_date) / EntityExtraction.one_day)
