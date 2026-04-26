import { Routes } from '@angular/router';
import { NewQuery } from './new-query/new-query';
import { QueryGenerated } from './query-generated/query-generated';

export const routes: Routes = [
  { path: '', component: NewQuery },
  { path: 'new-query', component: NewQuery },
  { path: 'query-generated', component: QueryGenerated }
];