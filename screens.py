import pygame as pg
from gui_base import *
from settings import *
from databasecontrol import *
from random import randint


def end():
    pg.quit()
    exit()


class _BaseScreen:
    def __init__(self, game):
        self._game = game
        self._screen = game.screen

        self._gui_surface = pg.Surface((WIDTH, HEIGHT))
        self._gui_surface.fill((124, 131, 143))

    def _run_self(self):
        while True:
            self._draw()
            self._screen.blit(self._gui_surface, (0,0))
            pg.display.flip()
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    end()
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_ESCAPE:
                        end()

    def _draw(self):
        pass

    def get_surface(self):
        return self._gui_surface


class StartScreen(_BaseScreen):
    def __init__(self, game):
        super().__init__(game)

        self.layout = GridLayout((0, 0), 5, 1)
        self.layout.add_element(Button(self, (0, 0), 750, 80, "START", WHITE, BLACK, game.game_loop), (0, 0))
        self.layout.add_element(Button(self, (0, 0), 750, 80, "LOGIN", WHITE, BLACK, game.show_login_screen), (0, 1))
        self.layout.add_element(Button(self, (0, 0), 750, 80, "LEADERBOARD", WHITE, BLACK, game.show_leaderboard_screen), (0, 2))
        self.layout.add_element(Button(self, (0, 0), 750, 80, "SETTINGS", WHITE, BLACK, game.show_settings_screen), (0, 3))
        self.layout.add_element(Button(self, (0, 0), 750, 80, "QUIT", WHITE, BLACK, end), (0, 4))

        self.layout.update_elements()

        self.layout.set_pos(((WIDTH - self.layout.get_width()) // 2, 0))
        self.layout.update_elements()

        self._run_self()

    def _run_self(self):
        while True:
            self._draw()
            self._screen.blit(self._gui_surface, (0,0))
            pg.display.flip()
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    end()
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_ESCAPE:
                        end()
                if event.type == pg.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        click_pos = pg.mouse.get_pos()
                        for button in self.layout:
                            if button.test_click(click_pos):
                                button.get_func()()
                                return

    def _draw(self):
        self.layout.draw()


class LoginScreen(_BaseScreen):
    def __init__(self, game):
        super().__init__(game)

        self._title = Label(self, (WIDTH/2-500, 0), 1000, 100, "LOGIN SCREEN", WHITE, (0,0,1))

        self.layout = GridLayout((0, 0), 4, 2)
        self._user_field = TextField(self, (0, 0), 750, 80, WHITE, (0,0,1))
        self._pass_field = TextField(self, (0, 0), 750, 80, WHITE, (0,0,1))
        self._login_button = Button(self, (0, 0), 750, 80, "LOGIN", WHITE, BLACK, self._login)
        self._create_account_button = Button(self, (0, 0), 750, 80, "CREATE ACCOUNT", WHITE, BLACK, self._create_account)
        self.layout.add_element(self._user_field, (1, 0))
        self.layout.add_element(self._pass_field, (1, 1))
        self.layout.add_element(self._login_button, (1, 2))
        self.layout.add_element(self._create_account_button, (1,3))
        self.layout.add_element(Label(self, (0,0), 500, 80, "USERNAME",WHITE,(0,0,1)),(0,0))
        self.layout.add_element(Label(self, (0, 0), 500, 80, "PASSWORD", WHITE, (0, 0, 1)), (0, 1))

        self.layout.update_elements()

        self.layout.set_pos(((WIDTH - self.layout.get_width()) // 2, 200))
        self.layout.update_elements()

        self._status_box = Label(self, (0,800),WIDTH,80,"",(124, 131, 143),(0,0,1))

        self._run_self()

    def _run_self(self):
        while True:
            self._draw()
            self._screen.blit(self._gui_surface, (0,0))
            pg.display.flip()
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    end()
                elif event.type == pg.KEYDOWN:
                    if event.key == pg.K_ESCAPE:
                        self._game.show_start_screen()
                    elif event.key == pg.K_BACKSPACE:
                        if self._user_field.get_active():
                            self._user_field.update_text("~")
                        elif self._pass_field.get_active():
                            self._pass_field.update_text("~")
                    else:
                        if self._user_field.get_active():
                            self._user_field.update_text(event.unicode)
                        elif self._pass_field.get_active():
                            self._pass_field.update_text(event.unicode)
                elif event.type == pg.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        click_pos = pg.mouse.get_pos()
                        if self._login_button.test_click(click_pos):
                            self._login_button.get_func()()
                        elif self._create_account_button.test_click(click_pos):
                            self._create_account_button.get_func()()
                        elif self._user_field.test_click(click_pos):
                            self._user_field.set_active(True)
                            self._pass_field.set_active(False)
                        elif self._pass_field.test_click(click_pos):
                            self._user_field.set_active(False)
                            self._pass_field.set_active(True)
                        else:
                            self._user_field.set_active(False)
                            self._pass_field.set_active(False)

    def _login(self):
        print("Trying to login")
        uname = self._user_field.get_text()
        pword = self._pass_field.get_text()
        if self._game.db.login(uname, pword):
            self._status_box.set_text("Login Success")
            self._user_field.set_text("")
            self._pass_field.set_text("")
        else:
            self._status_box.set_text("Login Fail")


    def _create_account(self):
        print("Trying to create account")
        uname = self._user_field.get_text()
        pword = self._pass_field.get_text()
        if self._game.db.add_user(uname, pword):
            self._status_box.set_text("Create Account Success")
            self._user_field.set_text("")
            self._pass_field.set_text("")
            self._game.db.login(uname, pword)
        else:
            self._status_box.set_text("Create Account Fail")

    def _draw(self):
        self._title.draw()
        self.layout.draw()
        self._status_box.draw()


class LeaderboardScreen(_BaseScreen):
    def __init__(self, game):
        super().__init__(game)

        self._reset_table()

        self._page_num = 0

        self.control_layout = GridLayout((1300, 50),3,1)
        self.control_layout.add_element(Label(self, (0, 0), 250, 50, "SORT BY", WHITE, (0, 0, 1)), (0, 0))
        self.control_layout.add_element(Button(self, (0,0), 250, 50, "SCORE", WHITE, (0, 0, 1), self._toggle_score_sort), (0, 1))
        self.control_layout.add_element(Button(self, (0, 0), 250, 50, "DATE", WHITE, (0, 0, 1), self._toggle_date_sort), (0, 2))

        self.control_layout.update_elements()

        self.control2_layout = GridLayout((1300, 100+self.control_layout.get_height()),1,2)
        self.control2_layout.add_element(Button(self, (0, 0), 115, 50, "<<", WHITE, (0, 0, 1), self._decrement_page), (0, 0))
        self.control2_layout.add_element(Button(self, (0, 0), 115, 50, ">>", WHITE, (0, 0, 1), self._increment_page), (1, 0))

        self.control2_layout.update_elements()

        self._dbc = databaseController()
        self._toggle_score_sort()

        self.last_sort_func = self._toggle_score_sort

        self._run_self()

    def _reset_table(self):
        self.table_layout = GridLayout((0, 0), 11, 3)
        self.table_layout.add_element(Label(self, (0, 0), 400, 50, "Username", WHITE, (0, 0, 1)), (0, 0))
        self.table_layout.add_element(Label(self, (0, 0), 400, 50, "Score", WHITE, (0, 0, 1)), (1, 0))
        self.table_layout.add_element(Label(self, (0, 0), 400, 50, "Date", WHITE, (0, 0, 1)), (2, 0))

        self.table_rows = []

        for count in range(10):
            row = (
                Label(self, (0, 0), 400, 50, "N/A", WHITE, (0, 0, 1)),
                Label(self, (0, 0), 400, 50, "N/A", WHITE, (0, 0, 1)),
                Label(self, (0, 0), 400, 50, "N/A", WHITE, (0, 0, 1))
            )
            self.table_rows.append(row)
            self.table_layout.add_element(row[0], (0, count + 1))
            self.table_layout.add_element(row[1], (1, count + 1))
            self.table_layout.add_element(row[2], (2, count + 1))

        self.table_layout.update_elements()

        self.table_layout.set_pos((50, 50))
        self.table_layout.update_elements()

    def _toggle_score_sort(self):
        self._reset_table()
        print("\n\n\n")
        for row_num, row_info in enumerate(self._dbc.get_all_scores_sc_desc(self._page_num)):
            print(row_info)
            self.table_rows[row_num][0].set_text(str(row_info[0]))
            self.table_rows[row_num][1].set_text(str(row_info[1]))
            self.table_rows[row_num][2].set_text(str(row_info[2]))

    def _toggle_date_sort(self):
        self._reset_table()
        for row_num, row_info in enumerate(self._dbc.get_all_scores_dt_desc(self._page_num)):
            self.table_rows[row_num][0].set_text(str(row_info[0]))
            self.table_rows[row_num][1].set_text(str(row_info[1]))
            self.table_rows[row_num][2].set_text(str(row_info[2]))

    def _increment_page(self):
        self._page_num += 1
        self.last_sort_func()

    def _decrement_page(self):
        if self._page_num != 0:
            self._page_num -= 1
            self.last_sort_func()

    def _run_self(self):
        while True:
            self._draw()
            self._screen.blit(self._gui_surface, (0,0))
            pg.display.flip()
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    end()
                elif event.type == pg.KEYDOWN:
                    if event.key == pg.K_ESCAPE:
                        self._game.show_start_screen()
                elif event.type == pg.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        click_pos = pg.mouse.get_pos()
                        if self.control_layout.get_element((0,1)).test_click(click_pos):
                            self._page_num = 0
                            self.control_layout.get_element((0,1)).get_func()()
                            self.last_sort_func = self.control_layout.get_element((0,1)).get_func()
                        elif self.control_layout.get_element((0,2)).test_click(click_pos):
                            self._page_num = 0
                            self.control_layout.get_element((0,2)).get_func()()
                            self.last_sort_func = self.control_layout.get_element((0, 2)).get_func()
                        elif self.control2_layout.get_element((0,0)).test_click(click_pos):
                            self.control2_layout.get_element((0,0)).get_func()()
                        elif self.control2_layout.get_element((1,0)).test_click(click_pos):
                            self.control2_layout.get_element((1,0)).get_func()()

    def _draw(self):
        self.control_layout.draw()
        self.control2_layout.draw()
        self.table_layout.draw()


class PauseScreen(_BaseScreen):
    def __init__(self, game):
        super().__init__(game)

        self._layout = GridLayout((0,0), 2, 1)

        self._resume_button = Button(self, (0,0), 600, 80, "RESUME", WHITE, (0,0,1), self._resume)
        self._quit_button = Button(self, (0,0), 600, 80, "QUIT", WHITE, (0,0,1), game.show_start_screen)

        self._layout.add_element(self._resume_button, (0,0))
        self._layout.add_element(self._quit_button, (0,1))

        self._layout.update_elements()

        self._layout.set_pos(((WIDTH - self._layout.get_width()) // 2, 100))
        self._layout.update_elements()

        self._run_self()

    def _run_self(self):
        while True:
            self._draw()
            self._screen.blit(self._gui_surface, (0,0))
            pg.display.flip()
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    end()
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_ESCAPE:
                        self._resume()
                elif event.type == pg.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        click_pos = pg.mouse.get_pos()
                        if self._resume_button.test_click(click_pos):
                            self._resume_button.get_func()()
                        elif self._quit_button.test_click(click_pos):
                            self._quit_button.get_func()()

    def _draw(self):
        self._layout.draw()

    def _resume(self):
        self._game.run()


class EndScreen(_BaseScreen):
    def __init__(self, game):
        super().__init__(game)

        self._layout = GridLayout((0, 0), 2, 1)

        self._layout.add_element(Label(self, (0,0), 900, 100, "YOU DIED", YELLOW, (0,0,1)), (0, 0))
        self._layout.add_element(Label(self, (0, 0), 900, 100, "SCORE:"+str(game.gui.get_element("scorecounter").get_score()), YELLOW, (0, 0, 1)), (0, 1))

        self._layout.update_elements()

        self._layout.set_pos(((WIDTH - self._layout.get_width()) // 2, 100))
        self._layout.update_elements()

        self._menu_button = Button(self, (0, 600), WIDTH, 150, "MENU", WHITE, BLACK, self._submit_score)

        self._run_self()

    def _run_self(self):
        while True:
            self._draw()
            self._screen.blit(self._gui_surface, (0, 0))
            pg.display.flip()
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    end()
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_ESCAPE:
                        self._submit_score()
                elif event.type == pg.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        click_pos = pg.mouse.get_pos()
                        if self._menu_button.test_click(click_pos):
                            self._menu_button.get_func()()

    def _draw(self):
        self._layout.draw()
        self._menu_button.draw()

    def _submit_score(self):
        if not self._game.db.check_login():
            self._game.db.login("guest","password")

        self._game.db.add_score(str(self._game.gui.get_element("scorecounter").get_score()))
        self._game.show_start_screen()


class ScoreScreen(_BaseScreen):
    def __init__(self, game):
        super().__init__(game)

        self._layout = GridLayout((0, 0), 3, 1)

        score_label = Label(self, (0, 0), WIDTH, 80, "CURRENT SCORE:"+str(game.gui.get_element("scorecounter").get_score()), YELLOW, (0, 0, 1))
        self._layout.add_element(score_label, (0, 0))
        scmul_label = Label(self, (0,0), WIDTH, 80, "SCORE MULTIPLIER:"+str(round(game._comp_diff_score,2)), YELLOW, (0,0,1))
        self._layout.add_element(scmul_label, (0, 1))
        fscore = round(game.gui.get_element("scorecounter").get_score() * game._comp_diff_score)
        game.gui.get_element("scorecounter").increment_score(fscore - game.gui.get_element("scorecounter").get_score())
        fscore_label = Label(self, (0,0), WIDTH, 80, "TOTAL SCORE:"+str(fscore), YELLOW, (0,0,1))
        self._layout.add_element(fscore_label, (0, 2))

        self._layout.update_elements()

        self._layout.set_pos(((WIDTH - self._layout.get_width()) // 2, 100))
        self._layout.update_elements()

        self._continue_button = Button(self, (0, 600), WIDTH, 150, "CONTINUE", WHITE, BLACK, game.next_level)

        self._run_self()

    def _run_self(self):
        while True:
            self._draw()
            self._screen.blit(self._gui_surface, (0, 0))
            pg.display.flip()
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    end()
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_ESCAPE:
                        self._game.next_level()
                elif event.type == pg.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        click_pos = pg.mouse.get_pos()
                        if self._continue_button.test_click(click_pos):
                            self._continue_button.get_func()()

    def _draw(self):
        self._layout.draw()
        self._continue_button.draw()



class SettingsScreen(_BaseScreen):
    def __init__(self, game):
        super().__init__(game)

        self._layout = GridLayout((0, 0), 2, 1)

        self._sound_button = Button(self, (0, 0), 500, 80, "UNMUTED", WHITE, (0, 0, 1), self._toggle_sound)
        self._layout.add_element(self._sound_button,(0, 0))
        self._menu_button = Button(self, (0,0),  500, 80, "MENU", WHITE, (0, 0, 1), self._game.show_start_screen)
        self._layout.add_element(self._menu_button,(0,1))

        self._layout.update_elements()

        self._layout.set_pos(((WIDTH - self._layout.get_width()) // 2, 100))
        self._layout.update_elements()

        self._run_self()

    def _toggle_sound(self):
        if self._game._s_heal.get_volume() == 0:
            self._game._s_heal.set_volume(1)
            self._sound_button.set_text("UNMUTED")
        elif self._game._s_heal.get_volume() == 1:
            self._game._s_heal.set_volume(0)
            self._sound_button.set_text("MUTED")

        self._layout.update_elements()

    def _run_self(self):
        while True:
            self._draw()
            self._screen.blit(self._gui_surface, (0, 0))
            pg.display.flip()
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    end()
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_ESCAPE:
                        self._game.show_start_screen()
                elif event.type == pg.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        click_pos = pg.mouse.get_pos()
                        if self._sound_button.test_click(click_pos):
                            self._sound_button.get_func()()
                        elif self._menu_button.test_click(click_pos):
                            self._menu_button.get_func()()

    def _draw(self):
        self._layout.draw()
