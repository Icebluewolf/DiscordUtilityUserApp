from discord import Bot, slash_command, ApplicationContext, OptionChoice, Option
import base64

BASES = [
    OptionChoice("Binary (2)", 2),
    OptionChoice("Trinary (3)", 3),
    OptionChoice("Octal (8)", 8),
    OptionChoice("Decimal (10)", 10),
    OptionChoice("Hexadecimal (16)", 16),
]

STRING_BASES = [
    OptionChoice("Binary (2)", 2),
    OptionChoice("Trinary (3)", 3),
    OptionChoice("Octal (8)", 8),
    OptionChoice("Decimal (10)", 10),
    OptionChoice("Hexadecimal (16)", 16),
    OptionChoice("Base64", 64),
    OptionChoice("Base32", 32),
    OptionChoice("Base85", 85),
]


async def convert_to_int(value: str, from_base: int) -> int | str:
    if from_base <= 36:
        converted = int(value, from_base)
    elif from_base == 32:
        converted = str(base64.b32decode(value))
    elif from_base == 64:
        converted = str(base64.b64decode(value))
    elif from_base == 85:
        converted = str(base64.b85decode(value))
    else:
        raise ValueError(f"Invalid Base {from_base}")
    if isinstance(converted, str):
        # Strip Off The b'' Of b'abc'
        converted = converted[2:-1]
    return converted


@slash_command(description="Convert Bases - Separate Individual Numbers With Tokens")
async def base_convert(
    ctx: ApplicationContext,
    value: Option(str, description="The Value To Convert"),
    to_base: Option(int, description="The Base To Convert To", choices=BASES),
    from_base: Option(int, description="The Base To Convert From", choices=BASES, required=False, default=10),
):
    results = []
    for v in value.split(" "):
        try:
            converted = await convert_to_int(v, from_base)
        except ValueError:
            await ctx.respond(f"Could Not Interpret `{v}` As Base `{from_base}`", ephemeral=True)
            return

        if to_base == 2:
            converted = bin(converted)
        elif to_base == 3:
            out = ""
            while converted != 0:
                out += str(converted % 3)
                converted = converted // 3
            converted = out[::-1]
        elif to_base == 8:
            converted = oct(converted)
        elif to_base == 10:
            converted = int(converted)
        elif to_base == 16:
            # Strip Off The 0x of 0x00
            converted = str(hex(converted))[2:]
        else:
            raise ValueError(f"Invalid Base {to_base}")
        results.append(str(converted))

    await ctx.respond(f"`{" ".join(results)}`\n-# `{value}` Converted From Base `{from_base}` To Base `{to_base}`")


@slash_command(descirption="Convert A Number In A Base To A String")
async def base_to_string(
    ctx: ApplicationContext,
    value: Option(str, description="The Value To Convert"),
    from_base: Option(int, description="The Base To Convert From", choices=STRING_BASES, required=False, default=10),
):
    results = ""
    for v in value.split(" "):
        try:
            converted = await convert_to_int(v, from_base)
        except ValueError:
            await ctx.respond(f"Could Not Interpret `{v}` As Base `{from_base}`", ephemeral=True)
            return
        if isinstance(converted, str):
            results += converted
        else:
            results += chr(converted)
    await ctx.respond(results)


def setup(bot: Bot):
    bot.add_application_command(base_convert)
    bot.add_application_command(base_to_string)
