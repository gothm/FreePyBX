"""
    This Source Code Form is subject to the terms of the Mozilla Public
    License, v. 2.0. If a copy of the MPL was not distributed with this
    file, You can obtain one at http://mozilla.org/MPL/2.0/.

    Software distributed under the License is distributed on an "AS IS"
    basis, WITHOUT WARRANTY OF ANY KIND, either express or implied. See the
    License for the specific language governing rights and limitations
    under the License.

    The Original Code is FreePyBX/VoiceWARE.

    The Initial Developer of the Original Code is Noel Morgan,
    Copyright (c) 2011-2012 VoiceWARE Communications, Inc. All Rights Reserved.

    http://www.vwci.com/

    You may not remove or alter the substance of any license notices (including
    copyright notices, patent notices, disclaimers of warranty, or limitations
    of liability) contained within the Source Code Form of the Covered Software,
    except that You may alter any license notices to the extent required to
    remedy known factual inaccuracies.

    Routes configuration

    The more specific and detailed routes should be defined first so they
    may take precedent over the more generic routes. For more information
    refer to the routes manual at http://routes.groovie.org/docs/
    """
from routes import Mapper

def make_map(config):
    """Create, configure and return the routes Mapper"""
    map = Mapper(directory=config['pylons.paths']['controllers'],
                 always_scan=config['debug'])
    map.minimization = False
    map.explicit = False

    # The ErrorController route (handles 404/500 error pages); it should
    # likely stay at the top, ensuring it can always be resolved
    map.connect('/error/{action}', controller='error')
    map.connect('/error/{action}/{id}', controller='error')

    map.connect('xml', '/configuration', controller='pbx', action='configuration')
    map.connect('xml', '/directory', controller='pbx', action='directory')
    map.connect('xml', '/dialplan', controller='pbx', action='dialplan')
    map.connect('mail', '/', controller='root', action='main')   
    map.connect('mail', '/main', controller='root', action='main')
    map.connect('mail', '/auth_user', controller='root', action='auth_user')
    map.connect('login', '/login', controller='root', action='login')
    map.connect('logout', '/logout', controller='root', action='logout')
    map.connect('message', '/pymp/send_message', controller='pymp', action='send_message')
    map.connect('mail', '/{controller}/{action}/{folder}/', controller='pymp', action='get_message_headers')
    map.connect('message', '/pymp/{action}/{folder}', controller='pymp', action='get_messages')
    map.connect('message', '/pymp/{action}/{folder}/{uid}', controller='pymp', action='get_message')
    map.connect('message', '/pymp/{action}/{folder}/{uid}/{filename}', controller='pymp', action='get_attachment')
    map.connect('message', '/pymp/{action}/{folder}', controller='pymp', action='get_message_headers')    

    map.connect('admin', '/admin/', controller='admin', action='index')
    map.connect('admin', '/admin/add_gateway', controller='admin', action='add_gateway')
    map.connect('admin', '/admin/add_context', controller='admin', action='add_context')
    map.connect('admin', '/admin/add_did', controller='admin', action='add_did')
    map.connect('admin', '/admin/add_customer', controller='admin', action='add_customer')
    map.connect('admin', '/admin/add_gateway', controller='admin', action='add_gateway')
    map.connect('admin', '/admin/add_profile', controller='admin', action='add_profile')
    map.connect('admin', '/admin/billing', controller='admin', action='billing')
    map.connect('admin', '/admin/login', controller='admin', action='login')

    map.connect('services', '/services/', controller='services', action='index')
    map.connect('services', '/services/service_list.html', controller='services', action='service_grid')
    map.connect('services', '/services/service_add.html', controller='services', action='service_add')
    map.connect('services', '/services/service_plans.html', controller='services', action='service_plan_grid')
    map.connect('services', '/services/voip_profiles.html', controller='services', action='voip_profile_grid')
    map.connect('services', '/services/voip_policies.html', controller='services', action='voip_policy_grid')

    map.connect('/flash_gateway', controller='flash_gateway')
    map.connect('root', '/pbx/user_edit.html', controller='root', action='user_edit')
    map.connect('root', '/pbx/ext_edit.html', controller='root', action='ext_edit')
    map.connect('root', '/pbx/extension_add.html', controller='root', action='extension_add')
    map.connect('root', '/pbx/user_add.html', controller='root', action='user_add')
    map.connect('root', '/pbx/broker_users.html', controller='root', action='broker_users')
    map.connect('pbx', '/pbx/extension_add.html', controller='root', action='extension_add')
    map.connect('pbx', '/pbx/cdr_ext_summary', controller='pbx', action='cdr_ext_summary')

    map.connect('provisioning', '/provisioning/{manufacturer}/{mac}/{model}.xml', controller='provisioning', action='get_config')

    map.connect('/{controller}/{action}')
    map.connect('/{controller}/{action}/{id}')

    return map
