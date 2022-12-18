import re
import pdftotext

from datetime import datetime
from typing import List, Optional

from model import Event


class PDFRegexFinder:
    @staticmethod
    def get_text_from_pdf(filename: str) -> str:
        text = ""

        with open(filename, "rb") as pdf_file:  # read, binary
            try:
                pdf = pdftotext.PDF(pdf_file)
                for page in pdf:
                    text += page
            except pdftotext.Error as err:
                raise OSError(filename)

        return text

    @staticmethod
    def find_matches(filename: str, regex: re.Pattern) -> list[re.Match]:
        text = PDFRegexFinder.get_text_from_pdf(filename)
        # print(text)
        return regex.findall(text)

    @staticmethod
    def find_events(filename: str) -> Optional[List[Event]]:
        REGEX = re.compile(
            r"""
                ((?:(?:Sunday|Monday|Tuesday|Wednesday|Thursday|Friday|Saturday)\s+){7})
                ((?:(?:\d{2}/\d{2}/\d{4})\s){7})
                (.*)
            """,
            (re.VERBOSE | re.MULTILINE),
        )
        matches = PDFRegexFinder.find_matches(filename, REGEX)

        events = []

        for week in matches:
            days_of_week = week[0].split()
            dates = week[1].split()
            shifts = week[2].split()
            assert len(days_of_week) == len(dates) == len(shifts)

            for i in range(len(days_of_week)):
                events.append(
                    Event(
                        day_of_week=days_of_week[i],
                        date=datetime.strptime(dates[i], "%m/%d/%Y").astimezone(),
                        shift=shifts[i],
                    )
                )

        return events
