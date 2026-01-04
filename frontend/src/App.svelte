<script>
  import { onMount } from 'svelte';
  import { Router, Route, Link } from 'svelte-routing';
  import { theme } from './lib/theme.js';

  import Login from './routes/Login.svelte';
  import BoardsList from './routes/BoardsList.svelte';
  import Board from './routes/Board.svelte';
  import NotFound from './routes/NotFound.svelte';

  onMount(() => {
    theme.init();
  });
</script>

<Router>
  <Route path="/login">
    <Login />
  </Route>

  <Route path="/boards">
    <BoardsList />
  </Route>

  <Route path="/boards/:id" let:params>
    <Board {params} />
  </Route>

  <Route path="/">
    <BoardsList />
  </Route>

  <Route path="*">
    <NotFound />
  </Route>
</Router>
