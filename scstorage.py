from io import BytesIO
from fastapi import FastAPI, Request, Response, status
from fastapi.responses import FileResponse
from PIL import Image
from pydantic import BaseModel
import minepi
import aiohttp
import uvicorn
import hashlib
import aiofiles.os
import time
import io

from main import config, shop



async def checkskin(skinraw):
    skin = Image.open(io.BytesIO(skinraw))
    w, h = skin.size
    return (w % 64 == 0 and h % 64 == 0) and (w <= 512 and h <= 512)


async def checkslim(skinraw):
    skin = Image.open(skinraw).convert(mode="RGBA")
    w, h = skin.size
    fraction = w / 8
    x, y = fraction * 6.75, fraction * 2.5
    pixel = skin.getpixel((int(x), int(y)))
    # x 54 y 20
    return pixel == (0, 0, 0, 0)


async def checkcape(caperaw):
    skin = Image.open(io.BytesIO(caperaw))
    w, h = skin.size
    return (w % 64 == 0 and h % 32 == 0) and (w <= 512 and h <= 512)

async def saveprofile(nickname, skinUrl):
        from main import db
        uuid=db.check_uuid(nickname)[1]["uuid"]
        async with aiohttp.ClientSession() as session:
            async with session.get(skinUrl) as resp:

                if await checkskin(await resp.read()):
                    with open(f'{config.web.skindir}/{uuid}.png', 'wb') as file:
                        file.write(await resp.read())
                    with open(f'{config.web.avatardir}/{uuid}.png', 'wb') as file:
                        s = minepi.Skin(raw_skin=Image.open(f'{config.web.skindir}/{uuid}.png'))
                        await s.render_head(vr=0, hr=0)
                        s.head.save(file)
                    return True
                else:
                    return False
                
async def savecape(nickname, capeUrl):
        from main import db
        uuid=db.check_uuid(nickname)[1]["uuid"]
        async with aiohttp.ClientSession() as session:
            async with session.get(capeUrl) as resp:

                if await checkcape(await resp.read()):
                    with open(f'{config.web.capedir}/{uuid}.png', 'wb') as file:
                        file.write(await resp.read())
                    return True
                else:
                    return False



app = FastAPI(docs_url=None, redoc_url=None)
class API:


    
    class Reqest_pay(BaseModel):
        type:str
        event:str
        object:dict
    #@app.middleware('http')
    #async def measure_time(request: Request, call_next):
    #    start = time.time()
    #    response = await call_next(request)
    #    end = time.time()
    #    res = end-start
    #    print(res)
    #    return response
    
    @app.post('/pay_check')
    async def post(response:Response, reqest:Reqest_pay):
        from cogs.event.check_pay import Check_pay
        if not shop.enabled:
            response = status.HTTP_404_NOT_FOUND
            return response
        
        if reqest.event == 'payment.succeeded':
            await Check_pay.check_pay(True, reqest.object['id'], int(float(reqest.object['amount']['value'])))
        else:
            await Check_pay.check_pay(False, reqest.object['id'], int(float(reqest.object['amount']['value'])))
        response = status.HTTP_200_OK
        return response
    
    @app.get('/storage')
    async def get(uuid:str):
        za_skin = {'url': f'{config.web.url}/storage/skin?uuid={uuid}', 'digest': None, 'metadata': {'model': None}}
        za_cape = {'url': f'{config.web.url}/storage/cape?uuid={uuid}', 'digest': None}
        linkSkin = f'{config.web.skindir}/{uuid}.png'
        linkCape = f'{config.web.capedir}/{uuid}.png'
        
        if await aiofiles.os.path.exists(linkSkin):
            za_skin['digest'] = hashlib.sha256(open(linkSkin, 'rb').read()).hexdigest()
            za_skin['metadata']['model'] = 'slim' if await checkslim(BytesIO(open(linkSkin, 'rb').read())) else 'classic'
        else:
            za_skin['digest'] = hashlib.sha256(open(config.web.defaultSkin, 'rb').read()).hexdigest()
            za_skin['metadata']['model'] = 'slim' if await checkslim(BytesIO(open(config.web.defaultSkin, 'rb').read())) else 'classic'

        if await aiofiles.os.path.exists(linkCape):
            za_cape['digest'] = hashlib.sha256(open(linkCape, 'rb').read()).hexdigest()
        else:
            za_cape['digest'] = hashlib.sha256(open(config.web.defaultCape, 'rb').read()).hexdigest()
        return {'SKIN':za_skin, 'CAPE':za_cape}
    
    @app.get('/storage/skin')
    async def storage(uuid:str):
        link = f'{config.web.skindir}/{uuid}.png'
        if await aiofiles.os.path.exists(link):
            return FileResponse(link)
        else:
            return FileResponse(config.web.defaultSkin)
        
    @app.get('/storage/cape')
    async def storage(uuid:str):
        link = f'{config.web.capedir}/{uuid}.png'
        if await aiofiles.os.path.exists(link):
            return FileResponse(link)
        else:
            return FileResponse(config.web.defaultCape)
        
    @app.get('/storage/avatar')
    async def storage(uuid:str):
        link = f'{config.web.avatardir}/{uuid}.png'
        if await aiofiles.os.path.exists(link):
            return FileResponse(link)
        else:
            return FileResponse(config.web.defaultAvatar)
        
    @app.head('/storage/skin')
    async def head(nickname:str, response:Response):
        response = status.HTTP_200_OK
        return response





    def server():
        uvicorn.run("scstorage:app", port=config.web.port, host=config.web.host, log_level="info", workers=3)
