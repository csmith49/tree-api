# The Zipper-HATEOAS Intersection: Elegant Tree Navigation for REST APIs

## TL;DR

Combine **zipper semantics** (focus + context, efficient navigation) with **HATEOAS** (hypermedia links, self-describing resources) to create an API where:
- Each node response includes its "context" (position in tree)
- Links encode all valid zipper operations from current position
- Server computes available moves; client follows links
- No client-side tree model needed - pure hypermedia navigation
- Stateless but feels stateful through rich link relations

## Core concept

A **zipper** represents: `Zipper = (Focus, Context)`
- **Focus**: Current node you're looking at
- **Context**: Everything else (path to root, siblings)

**HATEOAS** represents: `Resource = (Data, Links)`
- **Data**: The resource's properties
- **Links**: Available operations/transitions

**Zipper + HATEOAS** = `ZipperResource = (Focus, Context, Links)`
- **Focus**: Current node data
- **Context**: Position information (parent chain, siblings)
- **Links**: All valid zipper operations as hypermedia links

## Design: Zipper operations as link relations

### Standard zipper operations mapped to links

```json
{
  "id": "node-42",
  "description": "Implement authentication",
  "isLeaf": false,
  
  "_context": {
    "depth": 2,
    "siblingPosition": 1,
    "totalSiblings": 3,
    "hasChildren": true,
    "breadcrumbs": [
      {"id": "root", "description": "Build web app"},
      {"id": "node-10", "description": "Backend services"}
    ]
  },
  
  "_links": {
    "self": {
      "href": "/nodes/node-42"
    },
    
    "up": {
      "href": "/nodes/node-10",
      "title": "Parent: Backend services"
    },
    
    "down": {
      "href": "/nodes/node-42/children/first",
      "title": "First child: Set up JWT"
    },
    
    "left": {
      "href": "/nodes/node-41",
      "title": "Previous sibling: Database schema"
    },
    
    "right": {
      "href": "/nodes/node-43",
      "title": "Next sibling: API endpoints"
    },
    
    "root": {
      "href": "/nodes/root",
      "title": "Root: Build web app"
    },
    
    "next-dfs": {
      "href": "/nodes/node-42-child-1",
      "title": "Next in depth-first: Set up JWT"
    },
    
    "next-bfs": {
      "href": "/nodes/node-43",
      "title": "Next in breadth-first: API endpoints"
    },
    
    "children": {
      "href": "/nodes/node-42/children",
      "title": "All children"
    }
  },
  
  "_operations": {
    "modify": {
      "href": "/nodes/node-42",
      "method": "PATCH",
      "accepts": "application/json"
    },
    
    "expand": {
      "href": "/nodes/node-42/expand",
      "method": "POST",
      "accepts": "application/json",
      "available": false,
      "reason": "Node already has children"
    },
    
    "collapse": {
      "href": "/nodes/node-42/collapse",
      "method": "POST",
      "accepts": "application/json",
      "available": true
    },
    
    "delete": {
      "href": "/nodes/node-42",
      "method": "DELETE",
      "available": true
    }
  }
}
```

### Key insight: Links encode zipper's context

In a traditional zipper:
```haskell
data Loc a = Loc {
  focus :: Tree a,
  lefts :: [Tree a],      -- Elder siblings
  rights :: [Tree a],     -- Younger siblings  
  parents :: Path a       -- Context up the tree
}
```

In HATEOAS zipper:
```json
{
  "focus": { /* current node data */ },
  
  "_links": {
    "left": "...",    // First of lefts
    "right": "...",   // First of rights
    "up": "...",      // Parent from path
    "down": "..."     // First child
  }
}
```

The links **implicitly represent the zipper's context** without exposing the full structure.

## Navigation patterns

### 1. Depth-first traversal

**Traditional zipper code:**
```haskell
dfsNext :: Loc a -> Maybe (Loc a)
dfsNext loc = 
  down loc <|> right loc <|> up loc >>= right
```

**HATEOAS zipper - client just follows links:**
```python
def navigate_dfs(start_url):
    current = requests.get(start_url).json()
    
    while current:
        process(current)
        
        # Server computed next DFS step
        if 'next-dfs' in current['_links']:
            current = requests.get(
                current['_links']['next-dfs']['href']
            ).json()
        else:
            break  # Traversal complete
```

**No tree model needed!** Server computes DFS ordering, client follows links.

### 2. Breadth-first traversal

**Traditional zipper:** Requires queue, complex state management

**HATEOAS zipper:**
```python
def navigate_bfs(start_url):
    current = requests.get(start_url).json()
    
    while current:
        process(current)
        
        if 'next-bfs' in current['_links']:
            current = requests.get(
                current['_links']['next-bfs']['href']
            ).json()
        else:
            break
```

Server maintains BFS ordering computation; client stays simple.

### 3. Manual navigation (like zipper REPL)

**Traditional zipper REPL:**
```haskell
ghci> let z = fromTree myTree
ghci> z |> down |> right |> up |> left
```

**HATEOAS zipper - interactive client:**
```python
def interactive_navigate(start_url):
    current = requests.get(start_url).json()
    
    while True:
        display(current)
        available = current['_links'].keys()
        print(f"Available moves: {available}")
        
        move = input("Move: ")
        if move in current['_links']:
            current = requests.get(
                current['_links'][move]['href']
            ).json()
```

Discoverable navigation - see what's possible, pick direction.

## Zoom operations with HATEOAS

### Zoom in (expand leaf to subtree)

**Request:**
```http
POST /nodes/node-42/expand
Content-Type: application/json

{
  "children": [
    {"description": "Set up JWT library"},
    {"description": "Create auth middleware"},
    {"description": "Add login endpoint"}
  ]
}
```

**Response:**
```json
{
  "id": "node-42",
  "description": "Implement authentication",
  "isLeaf": false,
  
  "_context": {
    "depth": 2,
    "hasChildren": true,
    "childrenCount": 3
  },
  
  "_links": {
    "self": {"href": "/nodes/node-42"},
    "down": {
      "href": "/nodes/node-42-child-1",
      "title": "First child: Set up JWT library"
    },
    "children": {"href": "/nodes/node-42/children"}
  },
  
  "_operations": {
    "expand": {
      "href": "/nodes/node-42/expand",
      "method": "POST",
      "available": false,
      "reason": "Node already has children"
    },
    "collapse": {
      "href": "/nodes/node-42/collapse",
      "method": "POST",
      "available": true
    }
  }
}
```

Notice:
- `expand` operation now unavailable (node has children)
- `collapse` operation now available
- `down` link appears (wasn't there before)
- Links update to reflect new tree structure

### Zoom out (collapse subtree to leaf)

**Request:**
```http
POST /nodes/node-42/collapse
Content-Type: application/json

{
  "summary": "Implement authentication (3 steps complete)"
}
```

**Response:**
```json
{
  "id": "node-42",
  "description": "Implement authentication (3 steps complete)",
  "isLeaf": true,
  
  "_context": {
    "depth": 2,
    "hasChildren": false
  },
  
  "_links": {
    "self": {"href": "/nodes/node-42"},
    "up": {"href": "/nodes/node-10"},
    "left": {"href": "/nodes/node-41"},
    "right": {"href": "/nodes/node-43"}
  },
  
  "_operations": {
    "expand": {
      "href": "/nodes/node-42/expand",
      "method": "POST",
      "available": true
    },
    "collapse": {
      "href": "/nodes/node-42/collapse",
      "method": "POST",
      "available": false,
      "reason": "Node is already a leaf"
    }
  }
}
```

Notice:
- `down` link removed (no children)
- `expand` now available, `collapse` unavailable
- Description updated with summary
- Structure reflects leaf state

## Implementation: Server-side context computation

### Computing available moves

```python
def compute_links(node: Node, tree: Tree) -> dict:
    """Compute all valid zipper operations from current node."""
    links = {
        "self": {"href": f"/nodes/{node.id}"}
    }
    
    # Upward navigation
    if node.parent_id:
        parent = tree.get_node(node.parent_id)
        links["up"] = {
            "href": f"/nodes/{parent.id}",
            "title": f"Parent: {parent.description}"
        }
    
    # Downward navigation
    children = tree.get_children(node.id)
    if children:
        links["down"] = {
            "href": f"/nodes/{children[0].id}",
            "title": f"First child: {children[0].description}"
        }
        links["children"] = {
            "href": f"/nodes/{node.id}/children"
        }
    
    # Sibling navigation
    siblings = tree.get_siblings(node.id)
    node_idx = siblings.index(node)
    
    if node_idx > 0:
        prev_sibling = siblings[node_idx - 1]
        links["left"] = {
            "href": f"/nodes/{prev_sibling.id}",
            "title": f"Previous: {prev_sibling.description}"
        }
    
    if node_idx < len(siblings) - 1:
        next_sibling = siblings[node_idx + 1]
        links["right"] = {
            "href": f"/nodes/{next_sibling.id}",
            "title": f"Next: {next_sibling.description}"
        }
    
    # Traversal helpers
    links["next-dfs"] = {
        "href": f"/nodes/{compute_next_dfs(node, tree).id}"
    }
    links["next-bfs"] = {
        "href": f"/nodes/{compute_next_bfs(node, tree).id}"
    }
    
    # Root access
    links["root"] = {"href": "/nodes/root"}
    
    return links

def compute_operations(node: Node) -> dict:
    """Compute available operations based on node state."""
    ops = {
        "modify": {
            "href": f"/nodes/{node.id}",
            "method": "PATCH",
            "available": True
        },
        "delete": {
            "href": f"/nodes/{node.id}",
            "method": "DELETE",
            "available": not node.is_root
        }
    }
    
    # Zoom operations depend on state
    if node.is_leaf:
        ops["expand"] = {
            "href": f"/nodes/{node.id}/expand",
            "method": "POST",
            "available": True
        }
        ops["collapse"] = {
            "available": False,
            "reason": "Node is already a leaf"
        }
    else:
        ops["expand"] = {
            "available": False,
            "reason": "Node already has children"
        }
        ops["collapse"] = {
            "href": f"/nodes/{node.id}/collapse",
            "method": "POST",
            "available": True
        }
    
    return ops
```

### Building context breadcrumbs

```python
def compute_context(node: Node, tree: Tree) -> dict:
    """Build zipper-style context: breadcrumbs + position."""
    
    # Walk up to root
    breadcrumbs = []
    current = node.parent_id
    while current:
        parent = tree.get_node(current)
        breadcrumbs.insert(0, {
            "id": parent.id,
            "description": parent.description
        })
        current = parent.parent_id
    
    # Sibling position
    siblings = tree.get_siblings(node.id)
    position = siblings.index(node)
    
    return {
        "depth": len(breadcrumbs),
        "siblingPosition": position,
        "totalSiblings": len(siblings),
        "hasChildren": not node.is_leaf,
        "childrenCount": len(tree.get_children(node.id)),
        "breadcrumbs": breadcrumbs
    }
```

## Advantages of this intersection

### 1. **Discoverability** 🔍
Client doesn't need to know URL structure. Links tell you:
- What operations are possible
- Why operations might be unavailable
- What each link leads to (titles)

### 2. **Type safety through hypermedia** ✅
Server validates operations before presenting them:
- Can't collapse a leaf (link not present)
- Can't expand a branch (operation marked unavailable)
- Can't navigate where path doesn't exist

### 3. **Efficiency** ⚡
No need to fetch entire tree:
- Get only current node + context
- Follow links for navigation
- Server computes complex traversals (DFS, BFS)

### 4. **Immutability semantics** 🔒
Each request gets fresh view:
- No client-side mutation tracking
- Server handles consistency
- Perfect for concurrent access

### 5. **Stateless server, stateful feel** 🎯
- No server-side cursor/session needed
- Each response is complete
- Client experience feels continuous

### 6. **Incrementally explorable** 📚
Start simple, discover complexity:
```python
# Basic: just follow one link
response = get(url)
next_url = response['_links']['down']['href']

# Advanced: check available operations
if response['_operations']['expand']['available']:
    expand(response['_operations']['expand']['href'])

# Power user: full traversal
for node in dfs_traverse(root_url):
    process(node)
```

## Comparison with alternatives

### Pure REST (no zipper semantics)

```json
{
  "id": "node-42",
  "description": "...",
  "parentId": "node-10"
}
```

**Problems:**
- Client must construct URLs (`/nodes/{parentId}`)
- No indication of valid moves
- Client needs full tree model for navigation
- Traversal logic on client

### Pure zipper (no HATEOAS)

```json
{
  "focus": {"id": "node-42", "description": "..."},
  "lefts": [...],
  "rights": [...],
  "parents": [...]
}
```

**Problems:**
- Exposes internal structure
- Large payloads (entire context)
- Client must interpret structure
- Tight coupling to zipper representation

### Zipper + HATEOAS ✨

```json
{
  "id": "node-42",
  "description": "...",
  "_context": { /* minimal position info */ },
  "_links": { /* computed valid moves */ },
  "_operations": { /* available actions */ }
}
```

**Benefits:**
- Minimal payload
- Discoverable
- Decoupled
- Server-computed navigation

## Advanced patterns

### 1. Conditional link relations

Links can encode complex navigation rules:

```json
{
  "_links": {
    "next-incomplete": {
      "href": "/nodes/next?filter=incomplete",
      "title": "Next incomplete task"
    },
    "next-priority": {
      "href": "/nodes/next?order=priority",
      "title": "Next highest priority"
    }
  }
}
```

Server computes smart traversals based on business logic.

### 2. Link templates (RFC 6570)

For parameterized navigation:

```json
{
  "_links": {
    "search-descendants": {
      "href": "/nodes/{id}/search{?q,depth}",
      "templated": true
    }
  }
}
```

Client can customize without knowing URL structure.

### 3. Batch operations

Extend zoom to multiple nodes:

```json
{
  "_operations": {
    "expand-path": {
      "href": "/nodes/expand-path",
      "method": "POST",
      "body": {
        "nodeIds": ["node-1", "node-2", "node-3"]
      }
    }
  }
}
```

Server handles coordination, returns updated links.

### 4. Versioned navigation

Track tree versions through links:

```json
{
  "_links": {
    "self": {
      "href": "/nodes/node-42?version=5"
    },
    "previous-version": {
      "href": "/nodes/node-42?version=4"
    }
  }
}
```

Zipper navigation with time-travel!

## Implementation checklist

To build a zipper-HATEOAS API:

- [ ] **Core links**: up, down, left, right, root, self
- [ ] **Traversal links**: next-dfs, next-bfs
- [ ] **Context object**: breadcrumbs, position, depth
- [ ] **Operations object**: available actions + reasons
- [ ] **Link titles**: Human-readable descriptions
- [ ] **Conditional links**: Only include valid moves
- [ ] **Expand/collapse**: Zoom operations
- [ ] **Error responses**: Include links to valid states
- [ ] **Content negotiation**: Support JSON-LD, HAL, JSON:API
- [ ] **Cache headers**: ETag for node versions

## Summary: Why this intersection rocks 🎸

**Zippers give you:**
- Efficient navigation semantics
- Clear operation model (up/down/left/right)
- Immutability benefits
- Theoretical foundation

**HATEOAS gives you:**
- Discoverability
- Decoupling
- Evolvability
- Self-documenting API

**Together:** An API that's both theoretically elegant (zipper) and practically discoverable (HATEOAS), where navigation is efficient, operations are safe, and clients stay simple.

The server does the hard work (computing context, validating operations, determining next moves), exposing it through simple link relations that any client can follow.

**It's like having a smart guide through your tree, rather than a map you need to interpret yourself.** 🧭→🌳