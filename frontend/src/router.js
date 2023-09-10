import { createRouter, createWebHistory } from 'vue-router';

import Login from './views/Login.vue';
import Logout from './views/Logout.vue';
import Chat from './views/Chat.vue';
import Welcome from './views/Welcome.vue';
import ChatWindow from './components/ChatWindow.vue';
import Settings from './components/Settings.vue';
import Configure from './components/Configure.vue';
import Stack from './components/Stack.vue';
import Account from './components/Account.vue';
import ManageSpaces from './components/ManageSpaces.vue';
import Documents from './components/Documents.vue';
import Presets from './components/Presets.vue';
import Snippets from './components/Snippets.vue';
import Tools from './components/Tools.vue';
import Integrations from './components/Integrations.vue';
import Conversations from './components/Conversations.vue';
import Plugin from './components/Plugin.vue';
import Preset from './components/Preset.vue';

const routes = [
  {
    path: '/',
    component: Chat,
    children: [
      {
        path: '',
        name: 'ChatWindow',
        component: ChatWindow
      },
      {
        path: 'conversations',
        name: 'Conversations',
        component: Conversations

      },
      {
        path: 'documents/:id',
        name: 'Documents',
        component: Documents

      },
      {
        path: 'settings/:id',
        name: 'Settings',
        component: Settings

      },
      {
        path: 'config',
        name: 'Configure',
        component: Configure

      },
      {
        path: 'stack',
        name: 'Stack',
        component: Stack

      },
      {
        path: 'settings/:id/snippets',
        name: 'Snippets',
        component: Snippets

      },
      {
        path: 'settings/:id/tools',
        name: 'Tools',
        component: Tools

      },
      {
        path: 'presets',
        name: 'Presets',
        component: Presets

      },
      {
        path: 'preset/:id?',
        name: 'Preset',
        component: Preset

      },
      {
        path: 'plugins/:name',
        name: 'Plugin',
        component: Plugin
      },
      {
        path: 'integrations',
        name: 'Integrations',
        component: Integrations

      },
      {
        path: 'spaces',
        name: 'ManageSpaces',
        component: ManageSpaces

      },
      {
        path: 'account',
        name: 'Account',
        component: Account

      }
    ]
  },
  { path: '/welcome', name: 'Welcome', component: Welcome },
  { path: '/login', name: 'Login', component: Login },
  { path: '/logout', name: 'Logout', component: Logout },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;