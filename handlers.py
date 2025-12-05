import telebot
import time
import traceback
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

import db

BOT = None
ADMIN_IDS = []
REQUIRED_CHANNEL = ""
CONTACT_BOT = ""
OWNER_ID = 6000971026
temp_states = {}


def is_admin(uid):
    return uid == OWNER_ID or uid in ADMIN_IDS


def main_kb(uid):
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("📂 Earning Loots", callback_data="menu_loots"))
    kb.add(InlineKeyboardButton("❓ Doubt", callback_data="menu_doubt"))
    if is_admin(uid):
        kb.add(InlineKeyboardButton("👑 Admin Panel", callback_data="menu_admin"))
    return kb


def back_button(cb="back_main"):
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("⬅ Back", callback_data=cb))
    return kb


def admin_kb(uid):
    kb = InlineKeyboardMarkup()
    
    kb.add(InlineKeyboardButton("➕ Add Loot", callback_data="admin_add_loot"))
    kb.add(InlineKeyboardButton("➕ Add Owner Proof", callback_data="admin_add_owner_proof"))
    kb.add(InlineKeyboardButton("➕ Add Subscriber Proof", callback_data="admin_add_sub_proof"))
    kb.add(InlineKeyboardButton("🗂 List Loots", callback_data="admin_list_loots"))
    kb.add(InlineKeyboardButton("🗑 Delete Loot (full)", callback_data="admin_delete_loot"))
    kb.add(InlineKeyboardButton("🗑 Delete Videos/Proofs", callback_data="admin_delete_items"))
    kb.add(InlineKeyboardButton("📣 Broadcast", callback_data="admin_broadcast"))

    if uid == OWNER_ID:
        kb.add(InlineKeyboardButton("➕ Add Admin", callback_data="owner_add_admin"))
        kb.add(InlineKeyboardButton("➖ Remove Admin", callback_data="owner_remove_admin"))
        kb.add(InlineKeyboardButton("📋 View Admins", callback_data="owner_view_admins"))
    
    kb.add(InlineKeyboardButton("⬅ Back", callback_data="back_main"))
    return kb


def loots_kb():
    kb = InlineKeyboardMarkup()
    for lid, title, desc in db.get_loots():
        kb.add(InlineKeyboardButton(title, callback_data=f"open_loot||{lid}"))
    kb.add(InlineKeyboardButton("⬅ Back", callback_data="back_main"))
    return kb


def loot_actions_kb(lid):
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("🎥 Loot Video(s)", callback_data=f"view_media||{lid}||video"))
    kb.add(InlineKeyboardButton("📜 Owner Proof(s)", callback_data=f"view_media||{lid}||owner"))
    kb.add(InlineKeyboardButton("👥 Subscriber Proof(s)", callback_data=f"view_media||{lid}||subscriber"))
    kb.add(InlineKeyboardButton("⬅ Back", callback_data="menu_loots"))
    return kb


def send_media(chat_id, mobj, caption=None):
    try:
        if mobj.get("type") == "file":
            fid = mobj.get("file_id")
            try:
                BOT.send_video(chat_id, fid, caption=caption)
            except:
                try:
                    BOT.send_photo(chat_id, fid, caption=caption)
                except:
                    BOT.send_document(chat_id, fid, caption=caption)
        elif mobj.get("type") == "link":
            BOT.send_message(chat_id, f"{caption or ''}\n{mobj.get('link')}")
        elif mobj.get("type") == "text":
            BOT.send_message(chat_id, f"{caption or ''}\n{mobj.get('text')}")
    except Exception as ex:
        print("send_media error:", ex)


def check_joined(user_id):
    try:
        member = BOT.get_chat_member(REQUIRED_CHANNEL, user_id)
        if member.status in ["left", "kicked"]:
            return False
        return True
    except Exception as e:
        print("check_joined error:", e)
        return False


def parse_media(message):
    if message.content_type == "text":
        t = message.text.strip()
        if t.startswith("http://") or t.startswith("https://"):
            return {"type": "link", "link": t}
        else:
            return {"type": "text", "text": t}
    if message.content_type == "video":
        return {"type": "file", "file_id": message.video.file_id}
    if message.content_type == "photo":
        return {"type": "file", "file_id": message.photo[-1].file_id}
    if message.content_type == "document":
        return {"type": "file", "file_id": message.document.file_id}
    if message.content_type == "audio":
        return {"type": "file", "file_id": message.audio.file_id}
    return None


def setup_handlers(bot_instance, admin_ids, required_channel, contact_bot):
    global BOT, ADMIN_IDS, REQUIRED_CHANNEL, CONTACT_BOT, OWNER_ID

    BOT = bot_instance
    REQUIRED_CHANNEL = required_channel
    CONTACT_BOT = contact_bot
    
    ADMIN_IDS = admin_ids.copy()
    
    db_admins = db.get_admins()
    for a in db_admins:
        if a not in ADMIN_IDS:
            ADMIN_IDS.append(a)

    print("Loaded admins:", ADMIN_IDS)

    @BOT.message_handler(commands=["start"])
    def start_cmd(m):
        uid = m.from_user.id
        db.add_user(uid)
        
        if check_joined(uid):
            # User already joined - show welcome and main menu
            BOT.send_message(m.chat.id, "Welcome to LOOT WITH BTBB_BOT 🤩🤩🤩\n\nChoose an option:", reply_markup=main_kb(uid))
        else:
            # User hasn't joined - ask them to join first
            kb = InlineKeyboardMarkup()
            kb.add(InlineKeyboardButton("I Joined ✅", callback_data="verify_at_start"))
            kb.add(InlineKeyboardButton("⬅ Back", callback_data="back_main"))
            BOT.send_message(m.chat.id, f"Welcome to LOOT WITH BTBB_BOT 🤩🤩🤩\n\nPlease join {REQUIRED_CHANNEL} first to access earning loots.", reply_markup=kb)

    @BOT.callback_query_handler(func=lambda c: True)
    def cb(c):
        try:
            data = c.data
            uid = c.from_user.id

            if data == "back_main":
                BOT.edit_message_text("Back to main menu.", c.message.chat.id, c.message.message_id, reply_markup=main_kb(uid))
                return
          
            if data == "menu_doubt":
                MY_CONTACT = "@Bossssss191"
                BOT.edit_message_text(
                    f"❓ For doubts contact:\n{MY_CONTACT}\n{CONTACT_BOT}",
                    c.message.chat.id,
                    c.message.message_id,
                    reply_markup=back_button("back_main")
                )
                return

            if data == "owner_add_admin" and uid == OWNER_ID:
                temp_states[uid] = {"action": "add_admin"}
                BOT.send_message(uid, "Send Telegram USER ID of the new admin:")
                return

            if data == "owner_remove_admin" and uid == OWNER_ID:
                admins = db.get_admins()
                if not admins:
                    BOT.send_message(uid, "No admins to remove.")
                    return
                
                kb = InlineKeyboardMarkup()
                for a in admins:
                    kb.add(InlineKeyboardButton(str(a), callback_data=f"owner_do_remove||{a}"))
     
                BOT.send_message(uid, "Select an admin to remove:", reply_markup=kb)
                return

            if data.startswith("owner_do_remove||") and uid == OWNER_ID:
                _, admin_id = data.split("||", 1)
                admin_id = int(admin_id)

                db.remove_admin(admin_id)

                if admin_id in ADMIN_IDS:
                    ADMIN_IDS.remove(admin_id)

                BOT.send_message(uid, f"Admin {admin_id} removed successfully.")
                return


            if data == "owner_view_admins" and uid == OWNER_ID:
                admins = db.get_admins()
                text = "👑 Admin List:\n" + "\n".join(str(a) for a in admins) if admins else "No admins found."
                BOT.send_message(uid, text)
                return

            if data == "menu_loots":
                if not check_joined(uid):
                    kb2 = InlineKeyboardMarkup()
                    kb2.add(InlineKeyboardButton("I Joined ✅", callback_data="joined_check"))
                    kb2.add(InlineKeyboardButton("⬅ Back", callback_data="back_main"))
                    BOT.edit_message_text(f"Please join channel {REQUIRED_CHANNEL} first.", c.message.chat.id, c.message.message_id, reply_markup=kb2)
                    return
                loots = db.get_loots()
                if not loots:
                    BOT.answer_callback_query(c.id, "No loots yet.")
                    BOT.edit_message_text("No loots available currently.", c.message.chat.id, c.message.message_id, reply_markup=back_button("back_main"))
                    return
                BOT.edit_message_text("📂 Select a loot:", c.message.chat.id, c.message.message_id, reply_markup=loots_kb())
                return

            if data == "joined_check":
                if check_joined(uid):
                    BOT.answer_callback_query(c.id, "Verified ✅")
                    BOT.edit_message_text("Thanks — verified. Now choose a loot:", c.message.chat.id, c.message.message_id, reply_markup=loots_kb())
                else:
                    BOT.answer_callback_query(c.id, "Still not joined.")
                return

            if data == "verify_at_start":
                if check_joined(uid):
                    BOT.answer_callback_query(c.id, "Verified ✅")
                    BOT.edit_message_text("Welcome to LOOT WITH BTBB_BOT 🤩🤩🤩\n\nChoose an option:", c.message.chat.id, c.message.message_id, reply_markup=main_kb(uid))
                else:
                    BOT.answer_callback_query(c.id, "Still not joined.")
                return

            if data.startswith("open_loot||"):
                _, lid = data.split("||", 1)
                lid = int(lid)
                loot = db.get_loot(lid)
                if not loot:
                    BOT.answer_callback_query(c.id, "Not found.")
                    return
                BOT.edit_message_text(f"*{loot[1]}*", c.message.chat.id, c.message.message_id, parse_mode="Markdown", reply_markup=loot_actions_kb(lid))
                return

            if data.startswith("view_media||"):
                _, lid, kind = data.split("||", 2)
                lid = int(lid)
                loot = db.get_loot(lid)
                medias = db.get_media(lid, kind)

                if not medias:
                    BOT.answer_callback_query(c.id, "No items found.")
                    BOT.send_message(c.message.chat.id, "No items found.", reply_markup=loot_actions_kb(lid))
                    return

                BOT.answer_callback_query(c.id)

                # VIDEO LOOTS
                if kind == "video":
                    for idx, mrow in enumerate(medias):
                        mid, _, mtype, file_id, link, text_msg = mrow
                        caption = loot[2] if idx == 0 else None
                        send_media(
                            c.message.chat.id,
                            {
                                "type": mtype,
                                "file_id": file_id,
                                "link": link,
                                "text": text_msg
                            },
                            caption=caption
                        )
                    return

                # PROOFS (owner/sub)
                file_group = []
                other_msgs = []

                for mid, _, mtype, file_id, link, text_msg in medias:
                    if mtype == "file":
                        try:
                            file_group.append(telebot.types.InputMediaPhoto(file_id))
                        except:
                            file_group.append(telebot.types.InputMediaDocument(file_id))
                    else:
                        other_msgs.append({"type": mtype, "link": link, "text": text_msg})

                if file_group:
                    try:
                        BOT.send_media_group(c.message.chat.id, file_group)
                    except Exception as ex:
                        print("media_group error:", ex)

                for item in other_msgs:
                    if item["type"] == "link":
                        BOT.send_message(c.message.chat.id, item["link"])
                    else:
                        BOT.send_message(c.message.chat.id, item["text"])

                return

            if data == "menu_admin":
                if not is_admin(uid):
                    BOT.answer_callback_query(c.id, "Not admin.")
                    return
                BOT.edit_message_text("👑 Admin Panel", c.message.chat.id, c.message.message_id, reply_markup=admin_kb(uid))
                return

            if data == "admin_add_loot":
                if not is_admin(uid):
                    BOT.answer_callback_query(c.id, "Not admin.")
                    return
                temp_states[uid] = {"action": "add_loot", "step": "title"}
                BOT.send_message(uid, "➕ Send loot TITLE:")
                return

            if data == "admin_add_owner_proof":
                if not is_admin(uid):
                    return
                loots = db.get_loots()
                if not loots:
                    BOT.send_message(uid, "No loots yet.")
                    return
                kb = InlineKeyboardMarkup()
                for lid, title, _ in loots:
                    kb.add(InlineKeyboardButton(title, callback_data=f"admin_owner_choose||{lid}"))
                kb.add(InlineKeyboardButton("⬅ Back", callback_data="menu_admin"))
                BOT.send_message(uid, "Select loot for owner proof:", reply_markup=kb)
                return

            if data.startswith("admin_owner_choose||"):
                if not is_admin(uid):
                    return
                _, lid = data.split("||", 1)
                temp_states[uid] = {"action": "add_owner_proof", "loot_id": int(lid)}
                BOT.send_message(uid, "Send owner proof media/text/link. When done send /done.")
                return

            if data == "admin_add_sub_proof":
                if not is_admin(uid):
                    return
                loots = db.get_loots()
                if not loots:
                    BOT.send_message(uid, "No loots yet.")
                    return
                kb = InlineKeyboardMarkup()
                for lid, title, _ in loots:
                    kb.add(InlineKeyboardButton(title, callback_data=f"admin_sub_choose||{lid}"))
                kb.add(InlineKeyboardButton("⬅ Back", callback_data="menu_admin"))
                BOT.send_message(uid, "Select loot for subscriber proof:", reply_markup=kb)
                return

            if data.startswith("admin_sub_choose||"):
                if not is_admin(uid):
                    return
                _, lid = data.split("||", 1)
                temp_states[uid] = {"action": "add_sub_proof", "loot_id": int(lid)}
                BOT.send_message(uid, "Send subscriber proof media/text/link. When done send /done.")
                return

            if data == "admin_list_loots":
                if not is_admin(uid):
                    return
                loots = db.get_loots()
                if not loots:
                    BOT.send_message(uid, "No loots added yet.")
                    return
                kb = InlineKeyboardMarkup()
                for lid, title, _ in loots:
                    kb.add(InlineKeyboardButton(title, callback_data=f"admin_view_loot||{lid}"))
                kb.add(InlineKeyboardButton("⬅ Back", callback_data="menu_admin"))
                BOT.send_message(uid, "📦 Your loots:", reply_markup=kb)
                return

            if data.startswith("admin_view_loot||"):
                if not is_admin(uid):
                    return
                _, lid = data.split("||", 1)
                loot = db.get_loot(int(lid))
                medias_all = db.get_media(int(lid))
                BOT.edit_message_text(f"*{loot[1]}*\n\n{loot[2]}\n\nTotal media: {len(medias_all)}", c.message.chat.id, c.message.message_id, parse_mode="Markdown", reply_markup=admin_kb())
                return

            if data == "admin_delete_loot":
                if not is_admin(uid):
                    return
                loots = db.get_loots()
                if not loots:
                    BOT.send_message(uid, "No loots to delete.")
                    return
                kb = InlineKeyboardMarkup()
                for lid, title, _ in loots:
                    kb.add(InlineKeyboardButton(title, callback_data=f"confirm_delete_loot||{lid}"))
                kb.add(InlineKeyboardButton("⬅ Back", callback_data="menu_admin"))
                BOT.send_message(uid, "Select loot to delete:", reply_markup=kb)
                return

            if data.startswith("confirm_delete_loot||"):
                if not is_admin(uid):
                    return
                _, lid = data.split("||", 1)
                lid = int(lid)
                loot = db.get_loot(lid)
                if not loot:
                    BOT.answer_callback_query(c.id, "Loot not found.")
                    return
                BOT.send_message(
                    uid,
                    f"⚠️ Are you sure you want to delete *{loot[1]}* and all its media?",
                    parse_mode="Markdown",
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("✅ Confirm Delete", callback_data=f"do_delete_loot||{lid}")],
                        [InlineKeyboardButton("❌ Cancel", callback_data="menu_admin")],
                    ]),
                )
                return

            if data.startswith("do_delete_loot||"):
                if not is_admin(uid):
                    return
                _, lid = data.split("||", 1)
                db.delete_loot(int(lid))
                BOT.send_message(uid, "✔ Loot deleted.")
                return

            if data == "admin_delete_items":
                if not is_admin(uid):
                    return
                loots = db.get_loots()
                if not loots:
                    BOT.send_message(uid, "No loots yet.")
                    return
                kb = InlineKeyboardMarkup()
                for lid, title, _ in loots:
                    kb.add(InlineKeyboardButton(title, callback_data=f"choose_items_loot||{lid}"))
                kb.add(InlineKeyboardButton("⬅ Back", callback_data="menu_admin"))
                BOT.send_message(uid, "Select loot to manage its media:", reply_markup=kb)
                return

            if data.startswith("choose_items_loot||"):
                if not is_admin(uid):
                    return
                _, lid = data.split("||", 1)
                lid = int(lid)
                loot = db.get_loot(lid)
                if not loot:
                    BOT.send_message(uid, "Loot not found.")
                    return
                kb = InlineKeyboardMarkup()
                kb.add(InlineKeyboardButton("🗑 Delete specific video", callback_data=f"sel_del_media||{lid}||video"))
                kb.add(InlineKeyboardButton("🗑 Delete specific owner proof", callback_data=f"sel_del_media||{lid}||owner"))
                kb.add(InlineKeyboardButton("🗑 Delete specific subscriber proof", callback_data=f"sel_del_media||{lid}||subscriber"))
                kb.add(InlineKeyboardButton("⬅ Back", callback_data="admin_delete_items"))
                BOT.send_message(uid, f"Manage media for: *{loot[1]}*", parse_mode="Markdown", reply_markup=kb)
                return

            if data.startswith("sel_del_media||"):
                if not is_admin(uid):
                    return
                _, lid, kind = data.split("||", 2)
                lid = int(lid)
                medias = db.get_media(lid, kind)
                if not medias:
                    BOT.send_message(uid, "No items in this category.")
                    return
                kb = InlineKeyboardMarkup()
                for mid, _, mtype, file_id, link, text in medias:
                    label = mtype if mtype else "file"
                    kb.add(InlineKeyboardButton(f"{mid}. {label}", callback_data=f"confirm_del_media||{mid}"))
                kb.add(InlineKeyboardButton("⬅ Back", callback_data=f"choose_items_loot||{lid}"))
                BOT.send_message(uid, f"Select item to delete (loot id: {lid}, type: {kind}):", reply_markup=kb)
                return

            if data.startswith("confirm_del_media||"):
                if not is_admin(uid):
                    return
                _, mid = data.split("||", 1)
                mid = int(mid)
                row = db.get_media_by_id(mid)
                if not row:
                    BOT.answer_callback_query(c.id, "Item not found.")
                    return
                loot_id, kind, mtype, file_id, link, text_msg = row
                send_media(
                    c.from_user.id,
                    {"type": mtype, "file_id": file_id, "link": link, "text": text_msg},
                    caption=f"⚠️ You are about to delete this {kind} (ID:{mid}). Confirm?",
                )
                BOT.send_message(
                    c.from_user.id,
                    "✅ Confirm Delete / ❌ Cancel",
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("✅ Confirm", callback_data=f"do_del_media||{mid}")],
                        [InlineKeyboardButton("❌ Cancel", callback_data="menu_admin")],
                    ]),
                )
                return
            if data.startswith("do_del_media||"):
                if not is_admin(uid):
                    return
                _, mid = data.split("||", 1)
                db.delete_media(int(mid))
                BOT.send_message(uid, "✔ Media deleted.")
                return
            if data == "admin_broadcast":
                if not is_admin(uid):
                    return
                temp_states[uid] = {"action": "broadcast", "step": "message"}
                BOT.send_message(uid, "📣 Send broadcast message/media. When done send /done.")
                return
            BOT.answer_callback_query(c.id)
        except Exception as e:
            print("Callback error:", e, traceback.format_exc())
            BOT.answer_callback_query(c.id, "An error occurred")
    @BOT.message_handler(func=lambda m: m.from_user and is_admin(m.from_user.id) and not (m.text and m.text.startswith("/")), content_types=["text", "video", "photo", "document", "audio"])
    def handle_admin_inputs(m):
        uid = m.from_user.id

        st = temp_states.get(uid)
        if not st:
            return
    
        if st.get("action") == "add_admin" and uid == OWNER_ID:
            try:
                new_admin = int(m.text.strip())
                db.add_admin(new_admin)
                
                if new_admin not in ADMIN_IDS:
                    ADMIN_IDS.append(new_admin)
                    
                BOT.send_message(uid, f"✔ Added {new_admin} as new admin.")
                temp_states.pop(uid, None)
            except:
                BOT.send_message(uid, "Invalid ID! Send numeric Telegram user ID.")
            return
    def admin_msg(m):
        uid = m.from_user.id
        st = temp_states.get(uid)
        if not st:
            return
        action = st.get("action")
        if action == "add_loot":
            step = st.get("step")
            if step == "title":
                st["title"] = m.text.strip()
                st["step"] = "desc"
                temp_states[uid] = st
                BOT.send_message(uid, "Send description (text).")
                return
            if step == "desc":
                st["description"] = m.text.strip()
                st["step"] = "media"
                st["media"] = []
                temp_states[uid] = st
                BOT.send_message(uid, "Now send media (video/photo/document/link/text) one by one. When done send /done.")
                return
            if step == "media":
                obj = parse_media(m)
                if not obj:
                    BOT.send_message(uid, "Not a valid media/text/link. Send again or /done to finish.")
                    return
                st["media"].append(obj)
                temp_states[uid] = st
                BOT.send_message(uid, f"Saved item #{len(st['media'])}. Send more or /done.")
                return
        if action in ("add_owner_proof", "add_sub_proof"):
            loot_id = st.get("loot_id")
            obj = parse_media(m)
            if not obj:
                BOT.send_message(uid, "Not valid media/text/link.")
                return
            kind = "owner" if action == "add_owner_proof" else "subscriber"
            # Accumulate proofs in state first, then save on /done
            if "proofs" not in st:
                st["proofs"] = []
            st["proofs"].append(obj)
            temp_states[uid] = st
            BOT.send_message(uid, f"✔ {kind} proof #{len(st['proofs'])} added. Send more or /done to finish.")
            return
        if action == "broadcast":
            obj = parse_media(m)
            if not obj:
                BOT.send_message(uid, "Invalid message.")
                return
            users = db.get_users()
            sent = 0
            for user_id in users:
                try:
                    send_media(user_id, obj)
                    sent += 1
                    time.sleep(0.05)
                except:
                    pass
            BOT.send_message(uid, f"📣 Broadcast sent to {sent} users.")
            temp_states.pop(uid, None)
            return
    @BOT.message_handler(commands=["done"])
    def cmd_done(m):
        try:
            uid = m.from_user.id
            if not is_admin(uid):
                return
            st = temp_states.get(uid)
            if not st:
                BOT.send_message(uid, "No active operation.")
                return
            action = st.get("action")
            if action == "add_loot":
                title = st.get("title")
                desc = st.get("description", "")
                medias = st.get("media", [])
                loot_id = db.add_loot(title, desc)
                for mobj in medias:
                    db.add_media(loot_id, "video", mobj.get("type"), file_id=mobj.get("file_id"), link=mobj.get("link"), text_msg=mobj.get("text"))
                BOT.send_message(uid, f"✔ Loot '{title}' added with {len(medias)} media file(s).")
                temp_states.pop(uid, None)
                return
            if action in ("add_owner_proof", "add_sub_proof"):
                loot_id = st.get("loot_id")
                proofs = st.get("proofs", [])
                kind = "owner" if action == "add_owner_proof" else "subscriber"
                for pobj in proofs:
                    db.add_media(loot_id, kind, pobj.get("type"), file_id=pobj.get("file_id"), link=pobj.get("link"), text_msg=pobj.get("text"))
                BOT.send_message(uid, f"✔ {len(proofs)} {kind} proof(s) added to loot.")
                temp_states.pop(uid, None)
                return
            if action == "broadcast":
                BOT.send_message(uid, "✔ Operation completed.")
                temp_states.pop(uid, None)
                return
        except Exception as e:
            print(f"ERROR in cmd_done: {e}")
            traceback.print_exc()
            BOT.send_message(uid, f"❌ Error: {str(e)}")
    @BOT.message_handler(commands=["admin"])
    def cmd_admin(m):
        if not is_admin(uid):
            BOT.reply_to(m, "You are not an admin.")
            return
        BOT.send_message(uid, "👑 Admin Panel:", reply_markup=admin_kb(uid))
