import { NgModule } from '@angular/core';
import { PreloadAllModules, RouterModule, Routes } from '@angular/router';

import { ModeGuard } from "./shared/guard/mode/mode.guard";
import { AgentModeGuard } from "./shared/guard/agent_mode/agent_mode.guard";
import { LoggedinGuard } from "./shared/guard/loggedin/loggedin.guard";

const routes: Routes = [
  { path: '',
    redirectTo: 'home',
    pathMatch: 'full' },
  /* tabs */
  {
    path: 'tabs-enduser',
    loadChildren: () => import('./tabs-enduser/tabs-enduser.module').then( m => m.TabsEnduserPageModule)
  },
  {
    path: 'tabs-agent',
    loadChildren: () => import('./tabs-agent/tabs-agent.module').then( m => m.TabsAgentPageModule),
    //canActivate: [AgentModeGuard]
  },
  /* -- end tabs -- */
  /* capture */
  {
    path: 'login',
    loadChildren: () => import('./pages/capture/login/login.module').then( m => m.LoginPageModule),
    canActivate: [LoggedinGuard]
  },
  {
    path: 'register',
    loadChildren: () => import('./pages/capture/register/register.module').then( m => m.RegisterPageModule),
    canActivate: [LoggedinGuard]
  },
  {
    path: 'walkthrough',
    loadChildren: () => import('./pages/capture/walkthrough/walkthrough.module').then( m => m.WalkthroughPageModule)
  },
  {
    path: 'forgot-password',
    loadChildren: () => import('./pages/capture/forgot-password/forgot-password.module').then( m => m.ForgotPasswordPageModule),
    canActivate: [LoggedinGuard]
  },
  /* -- end capture -- */
  /* landing */
  {
    path: 'home',
    loadChildren: () => import('./pages/landing/home/home.module').then( m => m.HomePageModule),
    canActivate: [ModeGuard]
  },
  {
    path: 'enduser',
    loadChildren: () => import('./pages/landing/enduser/enduser.module').then( m => m.EnduserPageModule),
    canActivate: [ModeGuard]
  },
  {
    path: 'agent',
    loadChildren: () => import('./pages/landing/agent/agent.module').then( m => m.AgentPageModule),
    canActivate: [ModeGuard]
  },
  /* -- end landing -- */
  /* enduser */
  
  /* -- end enduser -- */
  /* chat-list */
  {
    path: 'chat-list',
    loadChildren: () => import('./pages/chat-list/chat-list.module').then( m => m.ChatListPageModule)
  },
  {
    path: 'chat',
    loadChildren: () => import('./pages/chat/chat.module').then( m => m.ChatPageModule)
  },
  /* -- end chat-list-- */
  /* agent */
  {
    path: 'payment',
    loadChildren: () => import('./pages/agent/payment/payment.module').then( m => m.PaymentPageModule)
  },
  {
    path: 'payments',
    loadChildren: () => import('./pages/agent/payments/payments.module').then( m => m.PaymentsPageModule)
  },
  {
    path: 'resolving',
    loadChildren: () => import('./pages/agent/resolving/resolving.module').then( m => m.ResolvingPageModule)
  },
  /* --end agent-- */
  /* stats */
  {
    path: 'approved',
    loadChildren: () => import('./pages/stats/approved/approved.module').then( m => m.ApprovedPageModule)
  },
  {
    path: 'pending',
    loadChildren: () => import('./pages/stats/pending/pending.module').then( m => m.PendingPageModule)
  },
  {
    path: 'reserved',
    loadChildren: () => import('./pages/stats/reserved/reserved.module').then( m => m.ReservedPageModule)
  },
  {
    path: 'resolved',
    loadChildren: () => import('./pages/stats/resolved/resolved.module').then( m => m.ResolvedPageModule)
  },
  {
    path: 'referred',
    loadChildren: () => import('./pages/stats/referred/referred.module').then( m => m.ReferredPageModule)
  },
  {
    path: 'cancelled',
    loadChildren: () => import('./pages/stats/cancelled/cancelled.module').then( m => m.CancelledPageModule)
  },
  /* --end stats-- */
  /* generic */
  {
    path: 'modal-popup',
    loadChildren: () => import('./pages/modals/modal-popup/modal-popup.module').then( m => m.ModalPopupPageModule)
  },
  {
    path: 'verify-email',
    loadChildren: () => import('./pages/verify-email/verify-email.module').then( m => m.VerifyEmailPageModule)
  },
  {
    path: 'update-password',
    loadChildren: () => import('./pages/update-password/update-password.module').then( m => m.UpdatePasswordPageModule)
  },
  {
    path: 'edit-profile',
    loadChildren: () => import('./pages/edit-profile/edit-profile.module').then( m => m.EditProfilePageModule)
  },
  {
    path: 'enquire',
    loadChildren: () => import('./pages/enquire/enquire.module').then( m => m.EnquirePageModule)
  },
  {
    path: 'support',
    loadChildren: () => import('./pages/support/support.module').then( m => m.SupportPageModule)
  },
  {
    path: 'modal-location',
    loadChildren: () => import('./pages/modals/modal-location/modal-location.module').then( m => m.ModalLocationPageModule)
  },
  {
    path: 'interests',
    loadChildren: () => import('./pages/interests/interests.module').then( m => m.InterestsPageModule)
  },
  {
    path: 'calendar',
    loadChildren: () => import('./pages/calendar/calendar.module').then( m => m.CalendarPageModule)
  },
  /* -- end generic -- */
  
];
@NgModule({
  imports: [
    RouterModule.forRoot(routes, { preloadingStrategy: PreloadAllModules, relativeLinkResolution: 'legacy' })
  ],
  exports: [RouterModule]
})
export class AppRoutingModule {}
