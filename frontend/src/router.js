import { createRouter, createWebHistory } from 'vue-router';

import Login from './views/Login.vue';
import Logout from './views/Logout.vue';
import Chat from './views/Chat.vue';
import Welcome from './views/Welcome.vue';
import ChatWindow from './components/ChatWindow.vue';
import Settings from './components/Settings.vue';
import Account from './components/Account.vue';
import ManageSpaces from './components/ManageSpaces.vue';
import Documents from './components/Documents.vue';
import Programs from './components/Programs.vue';
import Conversations from './components/Conversations.vue';

const routes = [
  { path: '/',
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
      path: 'programs',
      name: 'Programs',
      component: Programs

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