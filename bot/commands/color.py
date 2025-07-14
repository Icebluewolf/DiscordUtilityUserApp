#  Discord Utility User App
#  Copyright (c) 2025. Ice Wolfy
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Affero General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Affero General Public License for more details.
#
#  You should have received a copy of the GNU Affero General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.

from io import BytesIO
from zlib import compress, crc32

from discord import SlashCommandGroup, Option, ApplicationContext, Bot, File, MediaGalleryItem, Member
from discord.ui import Container, MediaGallery, View

from utils import component_factory as cf

group = SlashCommandGroup("color", "Utilities For Color")


def _create_png(pixels: list[list[tuple[int, ...]]]) -> BytesIO:
    height = len(pixels)

    if height == 0:
        raise ValueError("pixels cannot be an empty list")

    width = len(pixels[0])

    if width == 0:
        raise ValueError("pixels items cannot be an empty lists")

    if len(pixels[0][0]) == 3:
        alpha = False
    elif len(pixels[0][0]) == 4:
        alpha = True
    else:
        raise ValueError("Each Pixel In The 2D List Must Be RGB or RGBA")

    # PNG Header
    file = bytes([137, 80, 78, 71, 13, 10, 26, 10])
    # Width, Height, Bit Depth, Color Type, Compression Method, Filter Method, Interlace Method
    ihdr = (int.to_bytes(width, 4) +
            int.to_bytes(height, 4) +
            int.to_bytes(8, 1) +
            int.to_bytes(6, 1) +
            int.to_bytes(0, 1) +
            int.to_bytes(0, 1) +
            int.to_bytes(0, 1))
    ihdr_length = int.to_bytes(len(ihdr), 4)
    # Add Chunk Type
    ihdr = b"IHDR" + ihdr
    file += ihdr_length + ihdr + crc32(ihdr).to_bytes(4)

    idat = bytes()
    for y in pixels:
        # Filter Type For Scanline, R, G, B, A, R, G, B, A, ...
        idat += int.to_bytes(0, 1)
        for x in y:
            idat += int.to_bytes(x[0]) + int.to_bytes(x[1]) + int.to_bytes(x[2])
            if alpha:
                idat += int.to_bytes(x[3])
            else:
                idat += int.to_bytes(255)
    idat = compress(idat)
    idat_length = int.to_bytes(len(idat), 4)
    idat = b"IDAT" + idat
    file += idat_length + idat + crc32(idat).to_bytes(4)

    # IEND
    file += bytes([0, 0, 0, 0, 73, 69, 78, 68, 174, 66, 96, 130])

    return BytesIO(file)

def _create_single_color_png(color: tuple[int, ...], width: int, height: int) -> BytesIO:
    pixels = []
    for y in range(height):
        pixels.append([])
        for x in range(width):
            pixels[-1].append(color)
    return _create_png(pixels)

@group.command(name="hex", description="Sends Info About A Color From Hex")
async def from_hex(ctx: ApplicationContext, data: Option(str, name="hex", description="The Hex Value Of The Color")):
    # Save Leading Zeros
    zeros = len(data)
    try:
        data = hex(int(data.strip("# "), 16))[2:]
    except ValueError:
        return await ctx.respond(view=View(await cf.input_error("An Input Was Invalid", [f"`{data}` Could Not Be Interpreted As A Hex"])), ephemeral=True)
    zeros -= len(data)
    data = "0" * zeros + data

    if len(data) == 6:
        alpha = 255
    elif len(data) == 8:
        alpha = int(data[6:8], 16)
    else:
        return await ctx.respond(view=View(await cf.input_error("An Input Was Invalid", [f"The Input Hex Value Was Not 3 Or 4 Bytes"])), ephemeral=True)

    color = (int(data[0:2], 16), int(data[2:4], 16), int(data[4:6], 16), alpha)

    file = File(_create_single_color_png(color, 100, 100), filename="color.png")
    view = View(Container(MediaGallery(MediaGalleryItem("attachment://color.png"))))
    await ctx.respond(view=view, file=file)


@group.command(name="rgb", description="Sends Info About A Color From RGBA")
async def from_rgb(
        ctx: ApplicationContext,
        r: Option(int, name="red", min_value=0, max_value=255, description="The Red Component Of The Color"),
        g: Option(int, name="green", min_value=0, max_value=255, description="The Green Component Of The Color"),
        b: Option(int, name="blue", min_value=0, max_value=255, description="The Blue Component Of The Color"),
        a: Option(int, name="alpha", min_value=0, max_value=255, description="The Alpha Component Of The Color", default=255, required=False),
):
    file = File(_create_single_color_png((r, g, b, a), 100, 100), filename="color.png")
    view = View(Container(MediaGallery(MediaGalleryItem("attachment://color.png"))))
    await ctx.respond(view=view, file=file)


@group.command(name="user", description="Sends Info About The Color Of The Users Name")
async def from_user_role(ctx: ApplicationContext, member: Option(Member, name="user", description="The User To Get The Username Color Of")):
    print(member.roles)
    file = File(_create_single_color_png((r, g, b, a), 100, 100), filename="color.png")
    view = View(Container(MediaGallery(MediaGalleryItem("attachment://color.png"))))
    await ctx.respond(view=view, file=file)

def setup(bot: Bot):
    bot.add_application_command(group)
