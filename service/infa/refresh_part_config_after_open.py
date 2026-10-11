from pathlib import Path

from inventor_service import schedule_linked_parameters_refresh

CONFIG_PATH = Path(__file__).with_name("part_config.example.json")

schedule_linked_parameters_refresh(
    CONFIG_PATH,
    delay_seconds=2,
    skip_header=False,
)
