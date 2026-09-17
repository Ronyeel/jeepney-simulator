import tkinter as tk
from ui.theme import (
    GRASS_SUMO, ROAD_ASPHALT, ROAD_EDGE_WHITE, ROAD_LANE_DASH,
    ROAD_DIVIDER_WHITE, ROAD_DIVIDER_YELLOW,
    SIDEWALK_GRAY, SIDEWALK_CURB,
    CROSSWALK_WHITE, CROSSWALK_RED, CROSSWALK_GREEN,
    TRANSIT_BAY_HATCH, TRANSIT_SHED,
    FONT_MAP, FONT_MAP_TINY
)

class RoadScene(tk.Canvas):
    def __init__(self, parent, w, h):
        super().__init__(parent, width=w, height=h, bg=GRASS_SUMO,
                         highlightthickness=0, bd=0)
        self.W = w
        self.H = h

        self.road_top = int(h * 0.22)
        self.road_bot = int(h * 0.78)
        self.road_h = self.road_bot - self.road_top
        self.road_mid = (self.road_top + self.road_bot) // 2

        self.wb_lane_1 = self.road_top + int(self.road_h * 0.16)
        self.wb_lane_2 = self.road_top + int(self.road_h * 0.35)

        self.eb_lane_1 = self.road_mid + int(self.road_h * 0.15)
        self.eb_lane_2 = self.road_mid + int(self.road_h * 0.35)

        self.bay_x = int(w * 0.65)
        self.bay_y = self.eb_lane_2
        self.shed_x = self.bay_x - 130
        self.shed_y = self.road_bot + 24

        self.crosswalk_x = int(w * 0.18)

    def clear_dynamic(self):
        self.delete("dynamic")

    def draw_environment(self):
        self.delete("all")
        self._draw_grass()
        self._draw_sidewalks()
        self._draw_road_surface()
        self._draw_crosswalk()
        self._draw_transit_bay()
        self._draw_lane_markings()
        self._draw_scale_and_labels()

    def _draw_grass(self):
        W, H = self.W, self.H
        self.create_rectangle(0, 0, W, H, fill=GRASS_SUMO, outline="", tags="static")

    def _draw_sidewalks(self):
        W = self.W
        sw_h = 28
        self.create_rectangle(0, self.road_top - sw_h, W, self.road_top,
                               fill=SIDEWALK_GRAY, outline=SIDEWALK_CURB, tags="static")
        self.create_rectangle(0, self.road_bot, W, self.road_bot + sw_h + 30,
                               fill=SIDEWALK_GRAY, outline=SIDEWALK_CURB, tags="static")

        for x in range(0, W, 80):
            self.create_line(x, self.road_top - sw_h, x, self.road_top,
                             fill="#5f676e", width=1, tags="static")
            self.create_line(x, self.road_bot, x, self.road_bot + sw_h + 30,
                             fill="#5f676e", width=1, tags="static")

    def _draw_road_surface(self):
        W = self.W
        rt, rb, rm = self.road_top, self.road_bot, self.road_mid

        self.create_rectangle(0, rt, W, rb, fill=ROAD_ASPHALT, outline="", tags="static")

        self.create_line(0, rt, W, rt, fill=ROAD_EDGE_WHITE, width=3, tags="static")
        self.create_line(0, rb, W, rb, fill=ROAD_EDGE_WHITE, width=3, tags="static")

        self.create_line(0, rm - 2, W, rm - 2, fill=ROAD_DIVIDER_WHITE, width=2, tags="static")
        self.create_line(0, rm + 2, W, rm + 2, fill=ROAD_DIVIDER_WHITE, width=2, tags="static")

        dash_wb_split = (self.wb_lane_1 + self.wb_lane_2) // 2
        self.create_line(0, dash_wb_split, W, dash_wb_split,
                         fill=ROAD_LANE_DASH, width=2, dash=(28, 20), tags="static")

        dash_eb_split = (self.eb_lane_1 + self.eb_lane_2) // 2
        self.create_line(0, dash_eb_split, W, dash_eb_split,
                         fill=ROAD_LANE_DASH, width=2, dash=(28, 20), tags="static")

    def _draw_crosswalk(self):
        cx = self.crosswalk_x
        cw = 64
        rt, rb, rm = self.road_top, self.road_bot, self.road_mid

        self.create_rectangle(cx - 10, rt - 40, cx + cw + 10, rb + 40,
                               fill=SIDEWALK_GRAY, outline="", tags="static")
        self.create_rectangle(cx - 2, rt, cx + cw + 2, rb,
                               fill=ROAD_ASPHALT, outline="", tags="static")

        stripe_h = 10
        gap = 7
        curr_y = rt + 4
        while curr_y + stripe_h < rb - 4:
            self.create_rectangle(cx + 4, curr_y, cx + cw - 4, curr_y + stripe_h,
                                   fill=CROSSWALK_WHITE, outline="", tags="static")
            curr_y += stripe_h + gap

        self.create_rectangle(cx - 8, rt - 6, cx + cw + 8, rt,
                               fill=CROSSWALK_RED, outline="", tags="static")
        self.create_rectangle(cx - 8, rb, cx + cw + 8, rb + 6,
                               fill=CROSSWALK_RED, outline="", tags="static")

        self.create_line(cx + cw + 5, rt + 4, cx + cw + 5, rm - 4,
                         fill=CROSSWALK_GREEN, width=5, tags="static")
        self.create_line(cx - 5, rm + 4, cx - 5, rb - 4,
                         fill=CROSSWALK_GREEN, width=5, tags="static")

    def _draw_transit_bay(self):
        bx = self.bay_x
        bw = 180
        rb = self.road_bot
        by = self.bay_y

        self.create_rectangle(bx - 10, rb - 40, bx + bw + 10, rb,
                               fill="#1a1c1e", outline="", tags="static")
        self.create_line(bx - 10, rb, bx + bw + 10, rb,
                         fill=TRANSIT_BAY_HATCH, width=3, tags="static")
        self.create_line(bx - 10, rb - 40, bx + bw + 10, rb - 40,
                         fill=TRANSIT_BAY_HATCH, width=1, dash=(8, 8), tags="static")

        for hx in range(bx - 8, bx + bw, 18):
            self.create_line(hx, rb - 38, hx + 16, rb - 2,
                             fill=TRANSIT_BAY_HATCH, width=2, tags="static")

        sx = self.shed_x
        sy = self.shed_y
        sw = 130
        sh = 26
        self.create_rectangle(sx, sy, sx + sw, sy + sh,
                               fill=TRANSIT_SHED, outline="#475569", width=2, tags="static")
        self.create_text(sx + sw // 2, sy + sh // 2,
                         text="WAITING AREA",
                         font=FONT_MAP_TINY, fill="#f8fafc", tags="static")
        self.create_text(bx + bw // 2, rb + 14,
                         text="JEEPNEY LOADING BAY",
                         font=FONT_MAP_TINY, fill="#0f172a", tags="static")

    def _draw_lane_markings(self):
        cx = self.crosswalk_x + 90
        rm = self.road_mid

        arrow_xs = [cx + 80, cx + 320, cx + 580]
        for ax in arrow_xs:
            if ax < self.W - 80:
                y1 = self.wb_lane_1
                y2 = self.wb_lane_2
                self.create_line(ax, y1, ax - 30, y1, fill="#ffffff", width=3,
                                 arrow=tk.LAST, arrowshape=(10, 12, 4), tags="static")
                self.create_line(ax, y2, ax - 30, y2, fill="#ffffff", width=3,
                                 arrow=tk.LAST, arrowshape=(10, 12, 4), tags="static")

                ey1 = self.eb_lane_1
                ey2 = self.eb_lane_2
                self.create_line(ax - 30, ey1, ax, ey1, fill="#ffffff", width=3,
                                 arrow=tk.LAST, arrowshape=(10, 12, 4), tags="static")
                if ax + 40 < self.bay_x - 30 or ax > self.bay_x + 190:
                    self.create_line(ax - 30, ey2, ax, ey2, fill="#ffffff", width=3,
                                     arrow=tk.LAST, arrowshape=(10, 12, 4), tags="static")

    def _draw_scale_and_labels(self):
        W = self.W
        self.create_text(60, self.road_top - 14, text="TO DAET ◀",
                         font=FONT_MAP, fill="#ffffff", anchor=tk.W, tags="static")
        self.create_text(W - 60, self.road_bot + 14, text="TO MERCEDES  ▶",
                         font=FONT_MAP, fill="#ffffff", anchor=tk.E, tags="static")
