import misc

get_var = misc.get_var
set_vars = misc.set_vars


def reinit():
    global get_var, set_vars
    get_var = misc.get_var
    set_vars = misc.set_vars


def BOOSTX(drone, value):
    drone["velocity"][0] += value
    return f"Drone {drone['_id']} boosted at X axis by {value}!"


def BOOSTY(drone, value):
    drone["velocity"][1] += value
    return f"Drone {drone['_id']} boosted at Y axis by {value}!"


def FIRE(drone):
    return f"Drone {drone['_id']} fired!"


def SETFREQ(drone, frequency):
    return f"Drone {drone['_id']} freq set to {frequency}!"


def process_flight_plan(drone, curr_time):
    reinit()
    flight_plan = get_var(drone["_id"], "flight_plan")
    new_log = get_var(drone["_id"], "flight_log")

    if not flight_plan:
        return

    commands = flight_plan.split("\n")
    new_commands = ""

    for command in commands:
        if not command.strip():
            continue

        parts = command.split()
        if len(parts) == 0:
            continue

        expected_time = int(parts[0])
        if not (curr_time > expected_time or abs(curr_time - expected_time) < 0.2):
            new_commands += command + "\n"
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

    set_vars(drone["_id"], {"flight_plan": new_commands, "flight_log": new_log})
