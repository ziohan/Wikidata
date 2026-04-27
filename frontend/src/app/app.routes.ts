import { Routes } from '@angular/router';
import { NewQuery } from './new-query/new-query';
import { QueryGenerated } from './query-generated/query-generated';
import { Home } from './home/home';
import { LastQueries } from './last-queries/last-queries';

export const routes: Routes = [
  { path: '', component: Home },
  { path: 'new-query', component: NewQuery },
  { path: 'query-generated', component: QueryGenerated },
  { path: 'last-queries', component: LastQueries },
  { path: 'settings', component: Home },
  { path: 'history', component: Home }
];