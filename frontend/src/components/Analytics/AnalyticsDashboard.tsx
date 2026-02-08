import { useMemo } from 'react'
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer
} from 'recharts'
import { Box, Grid, GridItem, Heading, Text, HStack, useColorMode, Card } from '@chakra-ui/react'
import { format } from 'date-fns'

interface AnalyticsData {
  date: string
  views: number
  likes: number
  comments: number
  shares: number
  engagement_rate: number
}

interface PlatformPerformance {
  platform: string
  totalViews: number
  totalEngagement: number
  engagementRate: number
}

interface AnalyticsDashboardProps {
  data: AnalyticsData[]
  platformData: PlatformPerformance[]
}

const PLATFORM_COLORS: Record<string, string> = {
  youtube: '#FF0000',
  twitter: '#1DA1F2',
  instagram: '#E4405F',
  facebook: '#1877F2',
  linkedin: '#0A66C2',
  tiktok: '#000000',
  medium: '#000000',
  substack: '#FF6719'
}

export const AnalyticsDashboard: React.FC<AnalyticsDashboardProps> = ({
  data,
  platformData
}) => {
  const { colorMode } = useColorMode()
  const isDark = colorMode === 'dark'

  // Calculate totals
  const totals = useMemo(() => {
    return data.reduce(
      (acc, item) => ({
        views: acc.views + item.views,
        likes: acc.likes + item.likes,
        comments: acc.comments + item.comments,
        shares: acc.shares + item.shares
      }),
      { views: 0, likes: 0, comments: 0, shares: 0 }
    )
  }, [data])

  const avgEngagementRate = useMemo(() => {
    if (data.length === 0) return 0
    const sum = data.reduce((acc, item) => acc + item.engagement_rate, 0)
    return (sum / data.length).toFixed(2)
  }, [data])

  // Format data for charts
  const chartData = useMemo(() => {
    return data.map((item) => ({
      date: format(new Date(item.date), 'MMM dd'),
      views: item.views,
      engagement: item.likes + item.comments + item.shares,
      engagementRate: item.engagement_rate
    }))
  }, [data])

  const chartColors = {
    line: isDark ? '#60A5FA' : '#3B82F6',
    bar: isDark ? '#34D399' : '#10B981',
    text: isDark ? '#E5E7EB' : '#374151',
    grid: isDark ? '#374151' : '#E5E7EB'
  }

  return (
    <Box>
      {/* Summary Cards */}
      <Grid templateColumns="repeat(auto-fit, minmax(200px, 1fr))" gap={4} marginBottom={8}>
        <Card.Root>
          <Card.Body>
            <Text fontSize="sm" color="gray.500">
              Total Views
            </Text>
            <Heading size="2xl" marginTop={2}>
              {totals.views.toLocaleString()}
            </Heading>
          </Card.Body>
        </Card.Root>

        <Card.Root>
          <Card.Body>
            <Text fontSize="sm" color="gray.500">
              Total Likes
            </Text>
            <Heading size="2xl" marginTop={2} color="red.500">
              {totals.likes.toLocaleString()}
            </Heading>
          </Card.Body>
        </Card.Root>

        <Card.Root>
          <Card.Body>
            <Text fontSize="sm" color="gray.500">
              Total Comments
            </Text>
            <Heading size="2xl" marginTop={2} color="blue.500">
              {totals.comments.toLocaleString()}
            </Heading>
          </Card.Body>
        </Card.Root>

        <Card.Root>
          <Card.Body>
            <Text fontSize="sm" color="gray.500">
              Total Shares
            </Text>
            <Heading size="2xl" marginTop={2} color="green.500">
              {totals.shares.toLocaleString()}
            </Heading>
          </Card.Body>
        </Card.Root>

        <Card.Root>
          <Card.Body>
            <Text fontSize="sm" color="gray.500">
              Avg Engagement Rate
            </Text>
            <Heading size="2xl" marginTop={2} color="purple.500">
              {avgEngagementRate}%
            </Heading>
          </Card.Body>
        </Card.Root>
      </Grid>

      {/* Charts */}
      <Grid templateColumns={{ base: '1fr', lg: 'repeat(2, 1fr)' }} gap={6}>
        {/* Views Over Time */}
        <GridItem>
          <Card.Root>
            <Card.Header>
              <Heading size="md">Views Over Time</Heading>
            </Card.Header>
            <Card.Body>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" stroke={chartColors.grid} />
                  <XAxis
                    dataKey="date"
                    stroke={chartColors.text}
                    style={{ fontSize: '12px' }}
                  />
                  <YAxis stroke={chartColors.text} style={{ fontSize: '12px' }} />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: isDark ? '#1F2937' : '#FFFFFF',
                      border: `1px solid ${chartColors.grid}`,
                      borderRadius: '8px'
                    }}
                  />
                  <Legend />
                  <Line
                    type="monotone"
                    dataKey="views"
                    stroke={chartColors.line}
                    strokeWidth={2}
                    dot={{ fill: chartColors.line, r: 4 }}
                    activeDot={{ r: 6 }}
                  />
                </LineChart>
              </ResponsiveContainer>
            </Card.Body>
          </Card.Root>
        </GridItem>

        {/* Engagement Over Time */}
        <GridItem>
          <Card.Root>
            <Card.Header>
              <Heading size="md">Engagement Over Time</Heading>
            </Card.Header>
            <Card.Body>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" stroke={chartColors.grid} />
                  <XAxis
                    dataKey="date"
                    stroke={chartColors.text}
                    style={{ fontSize: '12px' }}
                  />
                  <YAxis stroke={chartColors.text} style={{ fontSize: '12px' }} />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: isDark ? '#1F2937' : '#FFFFFF',
                      border: `1px solid ${chartColors.grid}`,
                      borderRadius: '8px'
                    }}
                  />
                  <Legend />
                  <Bar dataKey="engagement" fill={chartColors.bar} radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </Card.Body>
          </Card.Root>
        </GridItem>

        {/* Engagement Rate Trend */}
        <GridItem>
          <Card.Root>
            <Card.Header>
              <Heading size="md">Engagement Rate Trend</Heading>
            </Card.Header>
            <Card.Body>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" stroke={chartColors.grid} />
                  <XAxis
                    dataKey="date"
                    stroke={chartColors.text}
                    style={{ fontSize: '12px' }}
                  />
                  <YAxis
                    stroke={chartColors.text}
                    style={{ fontSize: '12px' }}
                    tickFormatter={(value) => `${value}%`}
                  />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: isDark ? '#1F2937' : '#FFFFFF',
                      border: `1px solid ${chartColors.grid}`,
                      borderRadius: '8px'
                    }}
                    formatter={(value: number) => [`${value.toFixed(2)}%`, 'Engagement Rate']}
                  />
                  <Legend />
                  <Line
                    type="monotone"
                    dataKey="engagementRate"
                    name="Engagement Rate"
                    stroke="#A855F7"
                    strokeWidth={2}
                    dot={{ fill: '#A855F7', r: 4 }}
                    activeDot={{ r: 6 }}
                  />
                </LineChart>
              </ResponsiveContainer>
            </Card.Body>
          </Card.Root>
        </GridItem>

        {/* Platform Performance */}
        <GridItem>
          <Card.Root>
            <Card.Header>
              <Heading size="md">Performance by Platform</Heading>
            </Card.Header>
            <Card.Body>
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={platformData}
                    dataKey="totalViews"
                    nameKey="platform"
                    cx="50%"
                    cy="50%"
                    outerRadius={100}
                    label={({ platform, percent }) =>
                      `${platform}: ${(percent * 100).toFixed(0)}%`
                    }
                  >
                    {platformData.map((entry, index) => (
                      <Cell
                        key={`cell-${index}`}
                        fill={PLATFORM_COLORS[entry.platform.toLowerCase()] || '#718096'}
                      />
                    ))}
                  </Pie>
                  <Tooltip
                    contentStyle={{
                      backgroundColor: isDark ? '#1F2937' : '#FFFFFF',
                      border: `1px solid ${chartColors.grid}`,
                      borderRadius: '8px'
                    }}
                  />
                </PieChart>
              </ResponsiveContainer>
            </Card.Body>
          </Card.Root>
        </GridItem>
      </Grid>
    </Box>
  )
}
