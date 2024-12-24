import random


def print(*args, **kwargs):
    pass  # disable print


def BOOSTX(drone, value):
    drone["velocity"][0] += value
    return f"Drone {drone['id']} boosted at X axis by {value}!"


def BOOSTY(drone, value):
    drone["velocity"][1] += value
    return f"Drone {drone['id']} boosted at Y axis by {value}!"


def FIRE(drone):
    return f"Drone {drone['id']} fired!"


def SETFREQ(drone, frequency):
    return f"Drone {drone['id']} freq set to {frequency}!"


def get_expected_flight_log(flight_plan, curr_time, drone):
    new_log = ""

    commands = flight_plan.split("\n")
    for command in commands:
        if not command.strip():
            continue

        parts = command.split()
        if len(parts) == 0:
            continue

        expected_time = int(parts[0])
        if not (curr_time > expected_time or abs(curr_time - expected_time) < 0.2):
            continue

        command_name = parts[1]
        args = parts[2:]
        func = globals().get(command_name)
        if func and callable(func):
            try:
                typed_args = []
                if len(args) > 0 and args[0] == "[drone]":
                    typed_args.append(drone)
                    args = args[1:]

                typed_args.extend(
                    [
                        int(arg) if arg.replace("-", "", 1).isdigit() else arg
                        for arg in args
                    ]
                )
                new_log += str(func(*typed_args)) + "\n"
            except Exception as e:
                print(f"Error calling {command_name}: {e}", flush=True)
        else:
            print(f"Unknown command: {command_name}", flush=True)
    return new_log


def generate_plan(min_count, max_count):
    num_commands = random.randint(min_count, max_count)
    commands = []

    for _ in range(num_commands):
        command_type = random.choice(["BOOSTX", "BOOSTY", "FIRE", "SETFREQ"])

        if command_type == "BOOSTX":
            commands.append(
                f"{random.randint(0, 8)} BOOSTX [drone] {random.randint(-2, 2)}"
            )
        elif command_type == "BOOSTY":
            commands.append(
                f"{random.randint(0, 8)} BOOSTY [drone] {random.randint(-2, 2)}"
            )
        elif command_type == "FIRE":
            commands.append(f"{random.randint(0, 8)} FIRE [drone]")
        else:
            commands.append(
                f"{random.randint(0, 8)} SETFREQ [drone] {random.randint(10, 100)}"
            )

    return commands
