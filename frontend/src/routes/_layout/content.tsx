import { createFileRoute } from '@tanstack/react-router'
import { Box, Heading, Tabs, Container } from '@chakra-ui/react'
import { ContentCalendar } from '../../components/Content/ContentCalendar'
import { AnalyticsDashboard } from '../../components/Analytics/AnalyticsDashboard'
import { useState } from 'react'

export const Route = createFileRoute('/_layout/content')({
  component: ContentDashboard
})

function ContentDashboard() {
  const [activeTab, setActiveTab] = useState('calendar')

  // Mock data for analytics dashboard
  const mockAnalyticsData = [
    {
      date: '2026-02-01',
      views: 1250,
      likes: 187,
      comments: 45,
      shares: 23,
      engagement_rate: 15.2
    },
    {
      date: '2026-02-02',
      views: 1480,
      likes: 221,
      comments: 52,
      shares: 31,
      engagement_rate: 16.8
    },
    {
      date: '2026-02-03',
      views: 1320,
      likes: 198,
      comments: 48,
      shares: 27,
      engagement_rate: 15.9
    },
    {
      date: '2026-02-04',
      views: 1550,
      likes: 245,
      comments: 58,
      shares: 35,
      engagement_rate: 17.2
    },
    {
      date: '2026-02-05',
      views: 1420,
      likes: 212,
      comments: 51,
      shares: 29,
      engagement_rate: 16.4
    }
  ]

  const mockPlatformData = [
    { platform: 'YouTube', totalViews: 3250, totalEngagement: 486, engagementRate: 14.95 },
    { platform: 'Twitter', totalViews: 2120, totalEngagement: 378, engagementRate: 17.83 },
    { platform: 'Instagram', totalViews: 1890, totalEngagement: 412, engagementRate: 21.8 }
  ]

  return (
    <Container maxWidth="container.2xl" paddingY={8}>
      <Box marginBottom={6}>
        <Heading size="2xl">Content Automation</Heading>
      </Box>

      <Tabs.Root
        value={activeTab}
        onValueChange={(e) => setActiveTab(e.value)}
        variant="enclosed"
      >
        <Tabs.List>
          <Tabs.Trigger value="calendar">
            Content Calendar
          </Tabs.Trigger>
          <Tabs.Trigger value="analytics">
            Analytics
          </Tabs.Trigger>
        </Tabs.List>

        <Tabs.Content value="calendar" paddingTop={6}>
          <ContentCalendar
            onEventClick={(variantId) => {
              console.log('Event clicked:', variantId)
              // Navigate to content editor or open modal
            }}
          />
        </Tabs.Content>

        <Tabs.Content value="analytics" paddingTop={6}>
          <AnalyticsDashboard
            data={mockAnalyticsData}
            platformData={mockPlatformData}
          />
        </Tabs.Content>
      </Tabs.Root>
    </Container>
  )
}
