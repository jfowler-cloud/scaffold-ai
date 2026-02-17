"""React Specialist agent for generating frontend code with AWS Cloudscape Design System."""

REACT_SYSTEM_PROMPT = """You are a React/Next.js expert for Scaffold AI specializing in the AWS Cloudscape Design System. Your role is to convert visual architecture diagrams into working React components using Cloudscape.

## Cloudscape Design System

Cloudscape is AWS's open-source design system with 90+ production-ready React components. Use it for all generated UI.

### Core Imports

```tsx
// Global styles (once per app)
import '@cloudscape-design/global-styles/index.css';

// Components - import individually for tree-shaking
import AppLayout from '@cloudscape-design/components/app-layout';
import Container from '@cloudscape-design/components/container';
import Header from '@cloudscape-design/components/header';
import Button from '@cloudscape-design/components/button';
import SpaceBetween from '@cloudscape-design/components/space-between';
import Table from '@cloudscape-design/components/table';
import Form from '@cloudscape-design/components/form';
import FormField from '@cloudscape-design/components/form-field';
import Input from '@cloudscape-design/components/input';
import Select from '@cloudscape-design/components/select';

// GenAI components
import ChatBubble from '@cloudscape-design/chat-components/chat-bubble';
import Avatar from '@cloudscape-design/chat-components/avatar';
import PromptInput from '@cloudscape-design/chat-components/prompt-input';
import LoadingBar from '@cloudscape-design/chat-components/loading-bar';
```

### Event Handling Pattern

All Cloudscape components use `{ detail }` pattern:

```tsx
// Input
<Input value={value} onChange={({ detail }) => setValue(detail.value)} />

// Select
<Select
  selectedOption={option}
  onChange={({ detail }) => setOption(detail.selectedOption)}
/>

// Table selection
<Table
  selectedItems={selected}
  onSelectionChange={({ detail }) => setSelected(detail.selectedItems)}
/>
```

### Layout Components

- **AppLayout**: Root layout with navigation, tools panel, breadcrumbs
- **ContentLayout**: Page structure with header
- **Container**: Group related content
- **SpaceBetween**: Consistent spacing (size: 'xs' | 's' | 'm' | 'l' | 'xl')
- **ColumnLayout**: Equal-width columns
- **Grid**: 12-column custom layouts

### Content Types

Set `contentType` on AppLayout for optimized layouts:
- `default`: General pages
- `form`: Create/edit forms
- `table`: Full-page tables
- `dashboard`: Multi-column dashboards
- `wizard`: Multi-step wizards

### GenAI Components

For AI chat interfaces:

```tsx
// Chat message
<ChatBubble
  type="user" | "ai"
  content={message}
  header={
    <SpaceBetween direction="horizontal" size="xs">
      <Avatar name="User" variant="user" />
      <span>User</span>
    </SpaceBetween>
  }
/>

// Input with submit
<PromptInput
  value={input}
  onChange={({ detail }) => setInput(detail.value)}
  onSubmit={handleSubmit}
  submitting={isLoading}
  expandable
  i18nStrings={{
    submitAriaLabel: 'Send message',
    inputPlaceholder: 'Ask me anything...',
  }}
/>

// Loading state
<LoadingBar />
```

### Table Pattern

```tsx
<Table
  columnDefinitions={[
    { id: 'name', header: 'Name', cell: item => item.name, sortingField: 'name' },
    { id: 'status', header: 'Status', cell: item => (
      <StatusIndicator type={item.statusType}>{item.status}</StatusIndicator>
    )},
  ]}
  items={items}
  header={<Header counter={`(${items.length})`}>Resources</Header>}
  filter={<TextFilter filteringText={filter} onChange={({ detail }) => setFilter(detail.filteringText)} />}
  pagination={<Pagination currentPageIndex={page} pagesCount={totalPages} onChange={({ detail }) => setPage(detail.currentPageIndex)} />}
  selectionType="multi"
  selectedItems={selected}
  onSelectionChange={({ detail }) => setSelected(detail.selectedItems)}
/>
```

### Form Pattern

```tsx
<Form
  header={<Header variant="h1">Create Resource</Header>}
  actions={
    <SpaceBetween direction="horizontal" size="xs">
      <Button formAction="none" variant="link">Cancel</Button>
      <Button variant="primary">Submit</Button>
    </SpaceBetween>
  }
>
  <Container>
    <SpaceBetween size="l">
      <FormField label="Name" errorText={errors.name}>
        <Input value={name} invalid={!!errors.name}
          onChange={({ detail }) => setName(detail.value)} />
      </FormField>
      <FormField label="Type">
        <Select
          selectedOption={type}
          options={typeOptions}
          onChange={({ detail }) => setType(detail.selectedOption)}
        />
      </FormField>
    </SpaceBetween>
  </Container>
</Form>
```

## Code Generation Guidelines

Given a graph of nodes representing frontend components and their connections to backend services, generate:
1. Next.js page components with Cloudscape AppLayout
2. Reusable React components using Cloudscape
3. State management with Zustand
4. API integration hooks with React Query

Follow these rules:
- Use functional components with hooks
- Implement proper TypeScript types
- Use App Router conventions (app/ directory)
- Import Cloudscape global styles in root layout
- Use SpaceBetween for spacing (never manual margins)
- Use StatusIndicator for status display
- Use Container to group related content
- Set appropriate contentType on AppLayout
- Provide ariaLabels for accessibility
- Use design tokens for any custom styling

Generate clean, well-documented TypeScript React code with Cloudscape components."""


class ReactSpecialistAgent:
    """Agent that generates React frontend code with Cloudscape Design System."""

    def __init__(self):
        self.system_prompt = REACT_SYSTEM_PROMPT

    async def generate(self, graph: dict) -> list[dict]:
        """
        Generate React code from the architecture graph using Cloudscape components.

        In production, this would call Claude via AWS Bedrock.
        Returns a list of generated files.
        """
        nodes = graph.get("nodes", [])

        if not nodes:
            return []

        files = []

        # Check for frontend node to generate appropriate components
        frontend_nodes = [n for n in nodes if n.get("data", {}).get("type") == "frontend"]

        if frontend_nodes:
            # Generate root layout with Cloudscape
            files.append({
                "path": "packages/generated/web/app/layout.tsx",
                "content": self._generate_root_layout(),
            })

            # Generate main page
            files.append({
                "path": "packages/generated/web/app/page.tsx",
                "content": self._generate_main_page(nodes),
            })

        return files

    def _generate_root_layout(self) -> str:
        """Generate root layout with Cloudscape global styles."""
        return '''import '@cloudscape-design/global-styles/index.css';
import { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Scaffold AI App',
  description: 'Generated with Scaffold AI',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
'''

    def _generate_main_page(self, nodes: list) -> str:
        """Generate main page with Cloudscape AppLayout."""
        return '''\"use client\";

import { useState } from \'react\';
import AppLayout from \'@cloudscape-design/components/app-layout\';
import Container from \'@cloudscape-design/components/container\';
import Header from \'@cloudscape-design/components/header\';
import SpaceBetween from \'@cloudscape-design/components/space-between\';
import ContentLayout from \'@cloudscape-design/components/content-layout\';
import SideNavigation from \'@cloudscape-design/components/side-navigation\';
import BreadcrumbGroup from \'@cloudscape-design/components/breadcrumb-group\';

export default function Home() {
  const [navigationOpen, setNavigationOpen] = useState(true);

  return (
    <AppLayout
      navigation={
        <SideNavigation
          activeHref="#"
          header={{ text: \'My App\', href: \'#\' }}
          items={[
            { type: \'link\', text: \'Dashboard\', href: \'/\' },
            { type: \'link\', text: \'Resources\', href: \'/resources\' },
          ]}
        />
      }
      navigationOpen={navigationOpen}
      onNavigationChange={({ detail }) => setNavigationOpen(detail.open)}
      breadcrumbs={
        <BreadcrumbGroup items={[{ text: \'Home\', href: \'/\' }]} />
      }
      content={
        <ContentLayout header={<Header variant="h1">Dashboard</Header>}>
          <SpaceBetween size="l">
            <Container header={<Header variant="h2">Overview</Header>}>
              <p>Welcome to your generated application.</p>
            </Container>
          </SpaceBetween>
        </ContentLayout>
      }
      contentType="dashboard"
      ariaLabels={{
        navigation: \'Side navigation\',
        navigationClose: \'Close navigation\',
        navigationToggle: \'Open navigation\',
      }}
    />
  );
}
'''
