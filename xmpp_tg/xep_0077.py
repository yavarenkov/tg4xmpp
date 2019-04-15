from sleekxmpp import register_stanza_plugin, Iq, Callback, MatchXPath, ElementBase, ET
from sleekxmpp.plugins import BasePlugin
from sleekxmpp.plugins.xep_0004 import Form
from telethon.errors import SessionPasswordNeededError, PhoneNumberInvalidError

import xmpp_tg


class Registration(ElementBase):
    namespace = 'jabber:iq:register'
    name = 'query'
    plugin_attrib = 'register'
    interfaces = {'username', 'password', 'email', 'nick', 'name', 'first', 'last', 'address', 'city', 'state', 'zip',
                  'phone', 'url', 'date', 'misc', 'text', 'key', 'registered', 'remove', 'instructions'}
    sub_interfaces = interfaces


    def getRegistered(self):
        present = self.xml.find('{%s}registered' % self.namespace)
        return present is not None

    def getRemove(self):
        present = self.xml.find('{%s}remove' % self.namespace)
        return present is not None

    def setRegistered(self, registered):
        if registered:
            self.addField('registered')
        else:
            del self['registered']

    def setRemove(self, remove):
        if remove:
            self.addField('remove')
        else:
            del self['remove']

    def addField(self, name):
        itemXML = ET.Element('{%s}%s' % (self.namespace, name))
        self.xml.append(itemXML)


class xep_0077(BasePlugin):
    """
    XEP-0077 In-Band Registration
    """
    xmpptg: 'xmpp_tg.XMPPTelegram' = None

    def plugin_init(self):
        self.description = "XEP-0077: In-Band Registration (xmpp_tg)"
        self.xep = "0077"

        self.xmpp.registerHandler(
            Callback('In-Band Registration',
                     MatchXPath('{%s}iq/{jabber:iq:register}query' % self.xmpp.default_ns),
                     self._handle_stanza))
        register_stanza_plugin(Iq, Registration)

    def post_init(self):
        BasePlugin.post_init(self)
        self.xmpp['xep_0030'].add_feature("jabber:iq:register")

    def _handle_stanza(self, iq):
        if iq['type'] == 'get':
            self._handle_register_get(iq)
        elif iq['type'] == 'set':
            if iq['register']['remove']:
                return self._handle_register_delete(iq)
            return self._handle_register_set(iq)

    def _handle_register_set(self, iq):
        jid = iq['from'].bare
        form = iq['register']
        ''':type: Registration'''

        # x = form.xml.find('{jabber:x:data}x')
        # if x:
        #     form = self.xmpp.plugin['xep_0004'].build_form(x).get_values()  # TODO: unify this method to work both with xforms and without
        #     iq.error()
        #     iq['error']['text'] = 'unsupported form'
        #     return self.make_error(self.make_form(iq, instructions='instructions', form_data=form).reply(clear=False), '406', 'modify', 'not-acceptable', "forms are cool\n" * 20, clear=False).send()

        try:
            if form['misc'] and self.xmpp.tg_authenticate(jid, password=form['misc']):
                form.addField('registered')
            elif form['password'] and self.xmpp.tg_authenticate(jid, code=form['password']):
                form.addField('registered')

            elif form['phone']:
                try:
                    self.xmpp.tg_login(jid, form['phone'])
                except PhoneNumberInvalidError:
                    return self.make_error(iq, '406', 'modify', 'not-acceptable',
                                           "Phone number is invalid", clear=False).send()

                form.addField('password')
                form['instructions'] = 'Please enter one-time code as password'
                return self.make_error(iq, '406', 'modify', 'not-acceptable',
                                       "Additional information is required", clear=False).send()
            else:
                 return self.make_error(iq, '500', 'cancel', 'feature-not-implemented', 'unknown registration fields').send()

        except SessionPasswordNeededError:
            form.addField('misc')
            form['instructions'] = "Please enter 2FA password under 'misc'"
            self.make_error(iq, '406', 'modify', 'not-acceptable',
                            "Additional information is required", clear=False).send()

        iq.reply().setPayload(form.xml)
        iq.send()

    def _handle_register_delete(self, iq):
        self.xmpp.tg_logout()
        self.xmpp.event('unregistered_user', iq)
        iq.reply().send()

    def _handle_register_get(self, iq):
        jid = iq['from'].bare
        form_data = {'phone': None}

        user = self.xmpp.tg_user(jid)
        if user:
            form_data['phone'] = user.phone

        self.make_form(iq,
                       registered=user is not None,
                       instructions='Use your phone number to log in',
                       form_data=form_data).send()

    def make_form(self, request, registered=False, instructions=None, form_data=None):
        reg = request['register']
        reg.setRegistered(registered)

        if instructions:
            reg['instructions'] = instructions

        # f: Form = self.xmpp.plugin['xep_0004'].make_form(instructions=instructions)

        for field, data in (form_data or {}).items():
            if data:
                # Add field with existing data
                reg[field] = data
                # f.add_field(field, value=data)
            else:
                # Add a blank field
                reg.addField(field)
                # f.add_field(field)

        # reg.append(f)

        request.reply()
        request.setPayload(reg.xml)
        return request

    def make_error(self, iq, code, error_type, name, text='', clear=True):
        iq.reply(clear=clear).error()
        iq['error']['code'] = code
        iq['error']['type'] = error_type
        iq['error']['condition'] = name
        iq['error']['text'] = text
        iq.send()
        return iq
