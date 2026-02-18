from src.lib.prisma import prisma
from casp.layout import render_page


async def page():
    users = await prisma.user.find_many()
    return render_page(__file__, {
        "users": [user.to_dict() for user in users]
    })
