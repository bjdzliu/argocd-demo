from loguru import logger
import click
from pypdf import PdfReader

from yaku.autopilot_utils.results import DEFAULT_EVALUATOR, RESULTS, Result

class CLI:
    click_name = "pdf-checkbox-checker"
    click_setup = [
                   click.option('--file',type=str),
                   click.option('--field-name',type=str),
                   ]

    def click_command(file, field-name):
        print("hello")
