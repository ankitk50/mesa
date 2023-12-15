import json
from typing import Callable

import altair as alt
import solara

import mesa


def get_agent_data_from_coord_iter(data):
    for agent, (x, y) in data:
        if agent:
            agent_data = json.loads(
                json.dumps(agent[0].__dict__, skipkeys=True, default=str)
            )
            agent_data["x"] = x
            agent_data["y"] = y
            agent_data.pop("model", None)
            agent_data.pop("pos", None)
            yield agent_data


def create_grid(
    color: str | None = None,
    on_click: Callable[[mesa.Model, mesa.space.Coordinate], None] | None = None,
) -> Callable[[mesa.Model], solara.component]:
    return lambda model: Grid(model, color, on_click)


def Grid(model, color=None, on_click=None):
    if color is None:
        color = "unique_id:N"

    if color[-2] != ":":
        color = color + ":N"

    print(model.grid.coord_iter())

    data = solara.reactive(
        list(get_agent_data_from_coord_iter(model.grid.coord_iter()))
    )

    def update_data():
        data.value = list(get_agent_data_from_coord_iter(model.grid.coord_iter()))

    def click_handler(datum):
        if datum is None:
            return
        on_click(model, datum["x"], datum["y"])
        update_data()

    default_tooltip = [f"{key}:N" for key in data.value[0]]
    chart = (
        alt.Chart(alt.Data(values=data.value))
        .mark_rect()
        .encode(
            x=alt.X("x:N", scale=alt.Scale(domain=list(range(model.grid.width)))),
            y=alt.Y(
                "y:N",
                scale=alt.Scale(domain=list(range(model.grid.height - 1, -1, -1))),
            ),
            color=color,
            tooltip=default_tooltip,
        )
        .properties(width=600, height=600)
    )
    return solara.FigureAltair(chart, on_click=click_handler)
