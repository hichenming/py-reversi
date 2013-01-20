#!/bin/env python
# encoding=utf-8

#用apt-get install python-tornado安装的不是最新，有bug。要用 pip install tornado
#
#此方案采用websocket实现

import os
import random

import tornado
import json
from tornado import web, autoreload, websocket, ioloop, escape
from Config import Config
from datetime import timedelta
import logging

from tornado.options import define, options  

define("port", default=8888, help="Run server on a specific port", type=int)  

'''
    进入房间页面
'''
class EnterRoomHandler(web.RequestHandler):

    def get(self, room_name):
        self.render('index.html', config=Config,
            all_rooms_count = 10,)
        return
        

'''
    用websocket来与前端通信
'''
# class GameSocketHandler(tornado.websocket.WebSocketHandler):

#     socket_handlers = {}   #房间名-1:GameSocketHandler 一个房间每个人有一个值, 1用户订阅 room-1
#     all_rooms = {}  # 房间名:GameRoom
#     active_timeout = 600000 # 超时时间，超时后关闭房间

#     def open(self):

#         self.room_name = self.get_argument('room')
#         self.user_piece = int(self.get_argument('up'))
#         self.his_piece = self.user_piece == 1 and 2 or 1
#         self.room_name = self.room_name.encode('utf-8')
#         self.mykey = "%s-%d" % (self.room_name, self.user_piece)
#         self.hiskey = "%s-%d" % (self.room_name, self.his_piece)
#         self.is_active = False  #标志是否有活动，是否有人下棋，时间太长没人动，就关闭房间
#         if not self.room_name in GameSocketHandler.all_rooms:  #第一次进入房间
#             room = GameRoom(self.room_name, self.user_piece)
#             GameSocketHandler.all_rooms[self.room_name] = room
#             if isLog: logging.info('第一个进入')

#         if isLog: logging.info( "User %d has entered the room: %s" % (self.user_piece, self.room_name) )
#         if not self.mykey in GameSocketHandler.socket_handlers:
#             GameSocketHandler.socket_handlers[self.mykey] = self

#         GameSocketHandler.all_rooms[self.room_name].user_piece_ids.add(self.user_piece)

#         if self.hiskey in GameSocketHandler.socket_handlers: #对方也在线，游戏开始
#             if isLog:  logging.info( '游戏开始')
#             GameSocketHandler.socket_handlers[self.hiskey].write_message({'type':'on_gamestart'})
#             self.write_message({'type':'on_gamestart'})
#             GameSocketHandler.all_rooms[self.room_name].status = GameRoom.STATUS_GOING

#         self.chek_active = tornado.ioloop.PeriodicCallback(self._check_active_callback, GameSocketHandler.active_timeout)
#         self.chek_active.start()
#         return

#     def on_close(self):
#         try:   
#             GameSocketHandler.all_rooms[self.room_name].user_piece_ids.remove(self.user_piece)
#             if isLog: logging.info( 'User %d  has left the room: %s' % (self.user_piece, self.room_name) )

#             if not GameSocketHandler.all_rooms[self.room_name].user_piece_ids:  #房间没人了
#                 if isLog: logging.info( '移除房间: %s' % self.room_name )
#                 del GameSocketHandler.all_rooms[self.room_name]
#             else: #房间还有一个人，向这个人发通知
#                 if isLog: logging.info( 'Let the other guy know i\'m leaving.' )
#                 try:
#                     socket = GameSocketHandler.socket_handlers[self.hiskey]
#                     # 给对方发
#                     socket.write_message({'type':'offline'})

#                     GameSocketHandler.all_rooms[self.room_name].chess_game = ChessGame()
#                     GameSocketHandler.all_rooms[self.room_name].status = GameRoom.STATUS_WAITING
#                 except:
#                     logging.error( '_onclose_callback Exception.' )
#                     pass
#         except:
#             logging.error( 'on_close Exception.' )

#         if self.mykey in GameSocketHandler.socket_handlers: 
#             del GameSocketHandler.socket_handlers[self.mykey]
#         self.chek_active.stop()
#         return True

#     def on_message(self, message):
#         self.is_active = True
#         if isLog: logging.info( 'Room '+self.room_name+' websocket receive message: ' + message )
#         msg = json.loads(message)
#         if not u'type' in msg:
#             logging.error( 'Error. message has no type filed.')
#             return
#         msgtype = msg.get(u'type')
#         if msgtype == 'on_gamemove':
#             self._on_gamemove(msg)
#         elif msgtype == 'on_chat':
#             self._on_chat(msg)
#         return

#     def _on_chat(self, msg):
#         if not self.hiskey in GameSocketHandler.socket_handlers:
#             return False
#         socket = GameSocketHandler.socket_handlers[self.hiskey]
#         content = msg.get(u'content', '')
#         if not content:
#             return False
#         content = tornado.escape.xhtml_escape(content)
#         socket.write_message({'type':'on_chat', 'content':content})
#         return True

#     def _on_gamemove(self, msg):
#         self.is_active = True
#         row1 = msg.get('row1')
#         col1 = msg.get('col1')
#         row2 = msg.get('row2')
#         col2 = msg.get('col2')
#         room = GameSocketHandler.all_rooms[self.room_name]
#         ret = room.chess_game.moveTo(self.user_piece,int(row1),int(col1),int(row2), int(col2))
#         if not ret.result:
#             if isLog: logging.info('棋子移动失败.')
#             return False
#         else:
#             if room.chess_game.isGameOver:  #游戏结束
#                 if isLog:  logging.info( "Room: %s gameover." % self.room_name.encode('UTF-8') )
#                 socket = GameSocketHandler.socket_handlers[self.hiskey]
#                 socket.write_message({'type':'on_gameover'})
#                 self.write_message({'type':'on_gameover'})
#                 self.close()
#                 socket.close()
#             else:
#                 socket = GameSocketHandler.socket_handlers[self.hiskey]
#                 socket.write_message({'type':'on_gamemove', 'row1':row1, 'col1':col1, 'row2':row2, 'col2':col2})
#         return True

#     def allow_draft76(self):
#         return True

#     def _on_chat(self, msg):
#         if not self.hiskey in GameSocketHandler.socket_handlers:
#             return False
#         socket = GameSocketHandler.socket_handlers[self.hiskey]
#         content = msg.get(u'content', '')
#         if not content:
#             return False
#         socket.write_message({'type':'on_chat', 'content':content})
#         return True

#     def _check_active_callback(self):
#         if not self.is_active:
#             if isLog:  logging.info( '超时移除房间: %s' % self.room_name )
#             try:
#                 self.close()
#             except:
#                 pass

class RoomListHandler(web.RequestHandler):

    def get(self):
        self.render('rooms.html',
                    all_rooms_count = len(GameSocketHandler.all_rooms),
                    config = Config,
                    rooms = GameSocketHandler.all_rooms,
                    )

urls = [
        (r"/room-(.{1,200})", EnterRoomHandler),
        (r"/rooms", RoomListHandler),
        (r"/", RoomListHandler),
        # (r"/gamesocket", GameSocketHandler),
        ]

settings = dict(
        template_path = os.path.join(os.path.dirname(__file__), "templates"),
        static_path = os.path.join(os.path.dirname(__file__), "static"),
        cookie_secret = 'werwerwAW15Wwr-wrwe==dssdtfrwerter2t12',
        );

isLog = True

def main():
    # printrooms = tornado.ioloop.PeriodicCallback(printAllRooms, GameSocketHandler.active_timeout)
    # printrooms.start()
    tornado.options.parse_command_line() # -log_file_prefix=your complete path/test_log@8091.log
    application = web.Application(urls, **settings)
    application.listen(options.port)
    # tornado.autoreload.start(tornado.ioloop.IOLoop.instance()) # add this to enable autorestart
    tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    main()
