def motor_serializer(motor) -> dict:
    return{
        "id": str(motor["_id"]),
        "tipe_motor": motor["Tipe_Motor"],
        "harga": motor["Harga"]
    }

def motors_serializer(motors) -> list:
    return [motor_serializer(motor) for motor in motors]