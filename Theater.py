""" Theater Simulation

This module creates a theater simulation using the simpy library.
The simulation takes a user input and runs a simulation for SIM_TIME minutes. The result of the simulation is a
calculation of the average wait time experienced by the moviegoer during the simulation

"""
import random
import statistics

import simpy
wait_times: list = []
SIM_TIME: int = 10*60


class Theater(object):
    def __init__(self, th_env: simpy.Environment, num_cashiers: int, num_servers: int, num_ushers: int):
        self.env = th_env
        self.cashier = simpy.Resource(th_env, num_cashiers)
        self.server = simpy.Resource(th_env, num_servers)
        self.usher = simpy.Resource(th_env, num_ushers)

    def purchase_ticket(self):
        # Simulate ticket purchase which can take up to 3 minutes
        yield self.env.timeout(random.randint(1, 3))

    def check_ticket(self):
        # Simulate ticket verification which takes 3 seconds
        yield self.env.timeout(3 / 60)

    def purchase_food(self):
        # Simulate food/snack purchase which can take up to 5 minutes
        yield self.env.timeout(random.randint(1, 5))


def go_to_movies(mv_env: simpy.Environment, moviegoer: int, theater: Theater):
    arrival_time: float = mv_env.now
    print(f'Moviegoer #{moviegoer} arrived to the theater at time interval #{arrival_time}.')

    with theater.cashier.request() as request:
        print(f'Moviegoer #{moviegoer} started waiting for a cashier to '
              f'purchase a ticket at time interval #{mv_env.now}.')
        yield request
        yield mv_env.process(theater.purchase_ticket())
        print(f'Moviegoer #{moviegoer} purchased a ticket at time interval #{mv_env.now}')

    if random.choice([True, False]):
        with theater.server.request() as request:
            print(f'Moviegoer #{moviegoer} started waiting for a server to '
                  f'purchase snacks at time interval#{mv_env.now}.')
            yield request
            yield mv_env.process(theater.purchase_food())
        print(f'Moviegoer #{moviegoer} purchased snacks at time interval #{mv_env.now}.')

    with theater.usher.request() as request:
        print(f'Moviegoer #{moviegoer} is waiting for an usher to check their ticket.')
        yield request
        yield mv_env.process(theater.check_ticket())
        print(f'The ticket for moviegoer #{moviegoer} was checked at time interval #{mv_env.now}')

    wait_times.append(mv_env.now - arrival_time)


def run_theater(rn_env: simpy.Environment, num_cashiers: int, num_servers: int, num_ushers: int):
    theater = Theater(rn_env, num_cashiers, num_servers, num_ushers)
    moviegoer: int = 1

    # Simulate continuous line of moviegoers with a 12 second interval between each moviegoer
    while True:
        yield rn_env.timeout(12 / 60)
        moviegoer += 1
        env.process(go_to_movies(rn_env, moviegoer, theater))


def calculate_wait_times() -> tuple:
    average_wait = statistics.mean(wait_times)
    whole_minutes, frac_minutes = divmod(average_wait, 1)
    whole_seconds = frac_minutes / 60
    return round(whole_minutes), round(whole_seconds)


def get_user_input() -> list:
    num_cashiers = input('Enter number of cashiers: ')
    num_servers = input('Enter number of servers: ')
    num_ushers = input('Enter number of ushers: ')
    params = [num_cashiers, num_servers, num_ushers]
    if all(str(i).isdigit() for i in params):  # Check input is valid
        params = [int(x) for x in params]
    else:
        print(
            "Could not parse input. The simulation will use default values:",
            "\n1 cashier, 1 server, 1 usher.",
        )
        params = [1, 1, 1]

    return params


if __name__ == '__main__':
    param_list = get_user_input()
    env = simpy.Environment()
    run_process = env.process(run_theater(env, *param_list))
    env.run(until=SIM_TIME)

    minutes, seconds = calculate_wait_times()
    print(f'Average wait time is: {minutes} minutes and {seconds} seconds')
