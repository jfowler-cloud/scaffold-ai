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
            # Analyze architecture to determine what to generate
            has_auth = any(n.get("data", {}).get("type") == "auth" for n in nodes)
            has_api = any(n.get("data", {}).get("type") == "api" for n in nodes)
            has_database = any(n.get("data", {}).get("type") == "database" for n in nodes)
            has_storage = any(n.get("data", {}).get("type") == "storage" for n in nodes)

            # Generate root layout with Cloudscape
            files.append({
                "path": "packages/generated/web/app/layout.tsx",
                "content": self._generate_root_layout(),
            })

            # Generate main page based on architecture
            files.append({
                "path": "packages/generated/web/app/page.tsx",
                "content": self._generate_main_page(nodes, has_auth, has_api, has_database, has_storage),
            })

            # Generate auth components if auth exists
            if has_auth:
                files.append({
                    "path": "packages/generated/web/components/AuthProvider.tsx",
                    "content": self._generate_auth_provider(),
                })

            # Generate API hooks if API exists
            if has_api:
                files.append({
                    "path": "packages/generated/web/lib/api.ts",
                    "content": self._generate_api_hooks(nodes),
                })

            # Generate data table if database exists
            if has_database:
                files.append({
                    "path": "packages/generated/web/components/DataTable.tsx",
                    "content": self._generate_data_table(),
                })

            # Generate file upload if storage exists
            if has_storage:
                files.append({
                    "path": "packages/generated/web/components/FileUpload.tsx",
                    "content": self._generate_file_upload(),
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

    def _generate_main_page(self, nodes: list, has_auth: bool, has_api: bool, has_database: bool, has_storage: bool) -> str:
        """Generate main page with Cloudscape AppLayout based on architecture."""
        imports = ["useState"]
        if has_auth:
            imports.append("useEffect")
        
        components = [
            "AppLayout", "Container", "Header", "SpaceBetween", 
            "ContentLayout", "SideNavigation", "BreadcrumbGroup"
        ]
        
        if has_database:
            components.append("Button")
        
        nav_items = [
            "{ type: 'link', text: 'Dashboard', href: '/' }",
        ]
        
        if has_database:
            nav_items.append("{ type: 'link', text: 'Data', href: '/data' }")
        if has_storage:
            nav_items.append("{ type: 'link', text: 'Files', href: '/files' }")
        
        content_sections = []
        
        if has_auth:
            content_sections.append("""            <Container header={<Header variant="h2">Authentication</Header>}>
              <p>User authentication is configured with AWS Cognito.</p>
            </Container>""")
        
        if has_api:
            content_sections.append("""            <Container header={<Header variant="h2">API</Header>}>
              <p>REST API is available via AWS API Gateway.</p>
            </Container>""")
        
        if has_database:
            content_sections.append("""            <Container header={<Header variant="h2">Database</Header>}>
              <p>Data is stored in AWS DynamoDB.</p>
              <Button onClick={() => console.log('Load data')}>Load Data</Button>
            </Container>""")
        
        if has_storage:
            content_sections.append("""            <Container header={<Header variant="h2">Storage</Header>}>
              <p>Files are stored in AWS S3.</p>
            </Container>""")
        
        if not content_sections:
            content_sections.append("""            <Container header={<Header variant="h2">Overview</Header>}>
              <p>Welcome to your generated application.</p>
            </Container>""")

        return f'''\"use client\";

import {{ {", ".join(imports)} }} from 'react';
{chr(10).join(f"import {comp} from '@cloudscape-design/components/{comp.lower().replace('breadcrumbgroup', 'breadcrumb-group').replace('sidenavigation', 'side-navigation').replace('contentlayout', 'content-layout').replace('spacebetween', 'space-between').replace('applayout', 'app-layout')}';" for comp in components)}

export default function Home() {{
  const [navigationOpen, setNavigationOpen] = useState(true);

  return (
    <AppLayout
      navigation={{
        <SideNavigation
          activeHref="#"
          header={{{{ text: 'My App', href: '#' }}}}
          items={{[
            {", ".join(nav_items)}
          ]}}
        />
      }}
      navigationOpen={{navigationOpen}}
      onNavigationChange={{({{ detail }}) => setNavigationOpen(detail.open)}}
      breadcrumbs={{
        <BreadcrumbGroup items={{[{{ text: 'Home', href: '/' }}]}} />
      }}
      content={{
        <ContentLayout header={{<Header variant="h1">Dashboard</Header>}}>
          <SpaceBetween size="l">
{chr(10).join(content_sections)}
          </SpaceBetween>
        </ContentLayout>
      }}
      contentType="dashboard"
      ariaLabels={{{{
        navigation: 'Side navigation',
        navigationClose: 'Close navigation',
        navigationToggle: 'Open navigation',
      }}}}
    />
  );
}}
'''


    def _generate_auth_provider(self) -> str:
        """Generate auth provider component for Cognito."""
        return '''\"use client\";

import { createContext, useContext, useState, useEffect, ReactNode } from 'react';

interface AuthContextType {
  user: any | null;
  signIn: (username: string, password: string) => Promise<void>;
  signOut: () => Promise<void>;
  isLoading: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<any | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Check for existing session
    checkAuth();
  }, []);

  const checkAuth = async () => {
    try {
      // TODO: Implement Cognito session check
      setIsLoading(false);
    } catch (error) {
      setIsLoading(false);
    }
  };

  const signIn = async (username: string, password: string) => {
    // TODO: Implement Cognito sign in
    console.log('Sign in:', username);
  };

  const signOut = async () => {
    // TODO: Implement Cognito sign out
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, signIn, signOut, isLoading }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
}
'''

    def _generate_api_hooks(self, nodes: list) -> str:
        """Generate API hooks for data fetching."""
        api_nodes = [n for n in nodes if n.get("data", {}).get("type") == "api"]
        api_name = api_nodes[0].get("data", {}).get("label", "API") if api_nodes else "API"
        
        return f'''const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:3001';

export async function fetchData<T>(endpoint: string): Promise<T> {{
  const response = await fetch(`${{API_URL}}${{endpoint}}`);
  if (!response.ok) {{
    throw new Error(`{api_name} error: ${{response.status}}`);
  }}
  return response.json();
}}

export async function postData<T>(endpoint: string, data: any): Promise<T> {{
  const response = await fetch(`${{API_URL}}${{endpoint}}`, {{
    method: 'POST',
    headers: {{ 'Content-Type': 'application/json' }},
    body: JSON.stringify(data),
  }});
  if (!response.ok) {{
    throw new Error(`{api_name} error: ${{response.status}}`);
  }}
  return response.json();
}}

export async function deleteData(endpoint: string): Promise<void> {{
  const response = await fetch(`${{API_URL}}${{endpoint}}`, {{
    method: 'DELETE',
  }});
  if (!response.ok) {{
    throw new Error(`{api_name} error: ${{response.status}}`);
  }}
}}
'''

    def _generate_data_table(self) -> str:
        """Generate data table component for DynamoDB data."""
        return '''\"use client\";

import { useState } from 'react';
import Table from '@cloudscape-design/components/table';
import Header from '@cloudscape-design/components/header';
import Button from '@cloudscape-design/components/button';
import SpaceBetween from '@cloudscape-design/components/space-between';
import TextFilter from '@cloudscape-design/components/text-filter';
import Pagination from '@cloudscape-design/components/pagination';

interface DataItem {
  id: string;
  name: string;
  createdAt: string;
}

export function DataTable() {
  const [items, setItems] = useState<DataItem[]>([]);
  const [selectedItems, setSelectedItems] = useState<DataItem[]>([]);
  const [filterText, setFilterText] = useState('');
  const [currentPage, setCurrentPage] = useState(1);

  const filteredItems = items.filter(item =>
    item.name.toLowerCase().includes(filterText.toLowerCase())
  );

  return (
    <Table
      columnDefinitions={[
        { id: 'id', header: 'ID', cell: item => item.id, sortingField: 'id' },
        { id: 'name', header: 'Name', cell: item => item.name, sortingField: 'name' },
        { id: 'createdAt', header: 'Created', cell: item => item.createdAt },
      ]}
      items={filteredItems}
      selectionType="multi"
      selectedItems={selectedItems}
      onSelectionChange={({ detail }) => setSelectedItems(detail.selectedItems)}
      header={
        <Header
          counter={`(${filteredItems.length})`}
          actions={
            <SpaceBetween direction="horizontal" size="xs">
              <Button disabled={selectedItems.length === 0}>Delete</Button>
              <Button variant="primary">Create</Button>
            </SpaceBetween>
          }
        >
          Data Items
        </Header>
      }
      filter={
        <TextFilter
          filteringText={filterText}
          onChange={({ detail }) => setFilterText(detail.filteringText)}
          filteringPlaceholder="Find items"
        />
      }
      pagination={
        <Pagination
          currentPageIndex={currentPage}
          pagesCount={Math.ceil(filteredItems.length / 10)}
          onChange={({ detail }) => setCurrentPage(detail.currentPageIndex)}
        />
      }
      empty="No items found"
    />
  );
}
'''

    def _generate_file_upload(self) -> str:
        """Generate file upload component for S3."""
        return '''\"use client\";

import { useState } from 'react';
import Container from '@cloudscape-design/components/container';
import Header from '@cloudscape-design/components/header';
import SpaceBetween from '@cloudscape-design/components/space-between';
import Button from '@cloudscape-design/components/button';
import Alert from '@cloudscape-design/components/alert';
import ProgressBar from '@cloudscape-design/components/progress-bar';

export function FileUpload() {
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState('');

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
      setError('');
    }
  };

  const handleUpload = async () => {
    if (!file) return;

    setUploading(true);
    setProgress(0);
    setError('');

    try {
      // TODO: Get presigned URL from API
      // TODO: Upload to S3
      setProgress(100);
    } catch (err) {
      setError('Upload failed. Please try again.');
    } finally {
      setUploading(false);
    }
  };

  return (
    <Container header={<Header variant="h2">Upload File</Header>}>
      <SpaceBetween size="m">
        {error && <Alert type="error">{error}</Alert>}
        
        <input
          type="file"
          onChange={handleFileChange}
          disabled={uploading}
        />

        {file && (
          <div>
            <strong>Selected:</strong> {file.name} ({(file.size / 1024).toFixed(2)} KB)
          </div>
        )}

        {uploading && <ProgressBar value={progress} />}

        <Button
          variant="primary"
          onClick={handleUpload}
          disabled={!file || uploading}
          loading={uploading}
        >
          Upload to S3
        </Button>
      </SpaceBetween>
    </Container>
  );
}
'''
