from io import BytesIO
import uuid
from fastapi import FastAPI, Request, Response, status
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
from pydantic import BaseModel
import minepi
import aiohttp
import uvicorn
import hashlib
import aiofiles.os
import time

from main import config, shop, db



async def checkskin(skinraw):
    skin = Image.open(BytesIO(skinraw))
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
    skin = Image.open(BytesIO(caperaw))
    w, h = skin.size
    return (w % 64 == 0 and h % 32 == 0) and (w <= 512 and h <= 512)

async def saveprofile(nickname, skinUrl):
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
app.add_middleware(CORSMiddleware, allow_origins=["*"])
class API:


    
    class Reqest_pay(BaseModel):
        type:str
        event:str
        object:dict
    
    class Auth(BaseModel):
        login:str
        password:str

    class Join(BaseModel):
        accessToken:str
        userUUID:str
        serverID:str
    
    class HasJoined(BaseModel):
        username:str
        serverID:str

    class Profile(BaseModel):
        userUUID:str

    class Profiles(BaseModel):
        usernames:list
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

    @app.post('/authorization/auth')
    async def authorization(reqest:Auth):
        if db.connect():
            password = hashlib.sha256(reqest.password.encode('utf-8')).hexdigest()
            user = db.check_user(reqest.login, password)
            if user[1] != None:
                accessToken = uuid.uuid4().hex
                db.add_accessToken(accessToken, user[1]["uuid"])
                linkSkin = f'{config.web.skindir}/{user[1]["uuid"]}.png'
                if await aiofiles.os.path.exists(linkSkin):
                    slim_type = True if await checkslim(BytesIO(open(linkSkin, 'rb').read())) else False
                else:
                    slim_type = True if await checkslim(BytesIO(open(config.web.defaultSkin, 'rb').read())) else False
                return {
                "success": True,
                "result": {
                    "username": user[1]["username"],
                    "userUUID": user[1]["uuid"],
                    "accessToken": accessToken,
                    "isAlex": slim_type,
                    "skinUrl": f'{config.web.url}/storage/skin?uuid={user[1]["uuid"]}',
                    "capeUrl": f'{config.web.url}/storage/cape?uuid={user[1]["uuid"]}'
                }
                }
            return {
                "success": False,
                "error": "Неверный логин или пароль"
            }
        db.close()
        

    @app.post('/authorization/join')
    async def authorization(reqest:Join):
        if db.connect():
            if db.check_join(reqest.accessToken, reqest.userUUID)[1]['uuid'] == reqest.userUUID:
                db.add_serverID(reqest.serverID, reqest.userUUID)
                return {
                    "success": True,
                    "result": True
                }
            return {
                "success": False,
                "result": {"Неверные данные1"}
            }
        db.close()

    @app.post('/authorization/hasJoined')
    async def authorization(reqest:HasJoined):
        if db.connect():
            if db.check_serverID(reqest.serverID)[1]['username'] == reqest.username:
                user = db.check_uuid(reqest.username)
                linkSkin = f'{config.web.skindir}/{user[1]["uuid"]}.png'
                if await aiofiles.os.path.exists(linkSkin):
                    slim_type = True if await checkslim(BytesIO(open(linkSkin, 'rb').read())) else False
                else:
                    slim_type = True if await checkslim(BytesIO(open(config.web.defaultSkin, 'rb').read())) else False
                return {
                    "success": True,
                    "result": {
                        "userUUID": user[1]["uuid"],
                        "isAlex": slim_type,
                        "skinUrl": f'{config.web.url}/storage/skin?uuid={user[1]["uuid"]}',
                        "capeUrl": f'{config.web.url}/storage/cape?uuid={user[1]["uuid"]}'
                    }
                }
            return {
                "success": False,
                "result": {"Неверные данные2"}
            }
        db.close()

    @app.post('/authorization/profile')
    async def authorization(reqest:Profile):
        if db.connect():
            username = db.check_username(reqest.userUUID)
            if username[1] != None:
                linkSkin = f'{config.web.skindir}/{reqest.userUUID}.png'
                if await aiofiles.os.path.exists(linkSkin):
                    slim_type = True if await checkslim(BytesIO(open(linkSkin, 'rb').read())) else False
                else:
                    slim_type = True if await checkslim(BytesIO(open(config.web.defaultSkin, 'rb').read())) else False
                return {
                    "success": True,
                    "result": {
                        "username": username[1]['username'],
                        "isAlex": slim_type,
                        "skinUrl": f'{config.web.url}/storage/skin?uuid={reqest.userUUID}',
                        "capeUrl": f'{config.web.url}/storage/skin?uuid={reqest.userUUID}'
                    }
                }
            return {
                "success": False,
                "error": "Неверный UUID"
            }
        db.close()

    @app.post('/authorization/profiles')
    async def authorization(reqest:Profiles):
        if db.connect():
            response = []
            for list in db.check_profiles(reqest.usernames):
                response += {"id": list['uuid'], "name": list['username']}
            return {
                "success": True,
                "result": response
            }
        db.close()




    def server():
        uvicorn.run("scstorage:app", port=config.web.port, host=config.web.host, log_level="info", workers=3)
