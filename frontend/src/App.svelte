<script>
  import { onMount } from 'svelte';
  import { Router, Route } from 'svelte-routing';
  import { theme } from './lib/theme.js';

  import Landing from './routes/Landing.svelte';
  import Login from './routes/Login.svelte';
  import BoardsList from './routes/BoardsList.svelte';
  import Board from './routes/Board.svelte';
  import Organizations from './routes/Organizations.svelte';
  import Organization from './routes/Organization.svelte';
  import Admin from './routes/Admin.svelte';
  import Docs from './routes/Docs.svelte';
  import NotFound from './routes/NotFound.svelte';
  import ProtectedRoute from './lib/ProtectedRoute.svelte';
  import Header from './lib/Header.svelte';
  import Footer from './lib/Footer.svelte';
  import Pricing from './routes/Pricing.svelte';
  import About from './routes/About.svelte';
  import Contact from './routes/Contact.svelte';
  import Privacy from './routes/Privacy.svelte';
  import Terms from './routes/Terms.svelte';

  onMount(() => {
    theme.init();
  });
</script>

<svelte:head>
  <script>
    (function() {
      function updateBodyClass() {
        const path = window.location.pathname;
        if (path.startsWith('/boards') || path.startsWith('/organizations') || path.startsWith('/admin')) {
          document.body.classList.add('app-page');
        } else {
          document.body.classList.remove('app-page');
        }
      }
      updateBodyClass();
      window.addEventListener('popstate', updateBodyClass);
      const originalPushState = history.pushState;
      history.pushState = function() {
        originalPushState.apply(this, arguments);
        updateBodyClass();
      };
    })();
  </script>
</svelte:head>

<Router>
  <!-- Public pages -->
  <Route path="/" component={Landing} />
  <Route path="/docs" component={Docs} />
  <Route path="/docs/:section" let:params>
    <Docs {params} />
  </Route>
  <Route path="/login" component={Login} />
  <Route path="/pricing" component={Pricing} />
  <Route path="/about" component={About} />
  <Route path="/contact" component={Contact} />
  <Route path="/privacy" component={Privacy} />
  <Route path="/terms" component={Terms} />

  <!-- App pages: no Header/Footer -->
  <Route path="/boards">
    <ProtectedRoute>
      <BoardsList />
    </ProtectedRoute>
  </Route>

  <Route path="/boards/:id" let:params>
    <ProtectedRoute>
      <Board {params} />
    </ProtectedRoute>
  </Route>

  <Route path="/organizations">
    <ProtectedRoute>
      <Organizations />
    </ProtectedRoute>
  </Route>

  <Route path="/organizations/:id" let:params>
    <ProtectedRoute>
      <Organization {params} />
    </ProtectedRoute>
  </Route>

  <Route path="/admin" let:params>
    <ProtectedRoute>
      <Admin {params} />
    </ProtectedRoute>
  </Route>

  <Route path="/admin/:section" let:params>
    <ProtectedRoute>
      <Admin {params} />
    </ProtectedRoute>
  </Route>

  <Route path="*">
    <NotFound />
  </Route>
</Router>

<Header />
<Footer />

<style>
  :global(body.app-page) :global(.header),
  :global(body.app-page) :global(.footer) {
    display: none !important;
  }
</style>
