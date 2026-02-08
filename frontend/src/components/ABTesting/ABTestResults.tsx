import { useMemo } from 'react'
import {
  Box,
  Grid,
  GridItem,
  Heading,
  Text,
  HStack,
  VStack,
  Card,
  Badge,
  Progress,
  useColorMode
} from '@chakra-ui/react'
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell
} from 'recharts'
import { FaTrophy, FaChartLine } from 'react-icons/fa'

interface ABTestResult {
  test_id: string
  test_name: string
  status: 'draft' | 'running' | 'completed' | 'archived'
  goal: string
  variant_a: {
    views: number
    metric: number
    rate: number
  }
  variant_b: {
    views: number
    metric: number
    rate: number
  }
  statistical_analysis: {
    p_value: number | null
    is_significant: boolean
    confidence_level: number
    effect_size: number | null
    effect_interpretation: string
    confidence_interval: string | null
  }
  conclusion: {
    winner: string
    improvement_percentage: number
    sample_size_sufficient: boolean
    recommendation: string
  }
}

interface ABTestResultsProps {
  result: ABTestResult
}

export const ABTestResults: React.FC<ABTestResultsProps> = ({ result }) => {
  const { colorMode } = useColorMode()
  const isDark = colorMode === 'dark'

  // Prepare chart data
  const chartData = useMemo(() => {
    return [
      {
        variant: 'Variant A',
        rate: result.variant_a.rate * 100,
        views: result.variant_a.views,
        metric: result.variant_a.metric
      },
      {
        variant: 'Variant B',
        rate: result.variant_b.rate * 100,
        views: result.variant_b.views,
        metric: result.variant_b.metric
      }
    ]
  }, [result])

  const winnerColor =
    result.conclusion.winner === 'Variant A'
      ? '#3B82F6'
      : result.conclusion.winner === 'Variant B'
      ? '#10B981'
      : '#6B7280'

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'running':
        return 'blue'
      case 'completed':
        return 'green'
      case 'draft':
        return 'gray'
      case 'archived':
        return 'orange'
      default:
        return 'gray'
    }
  }

  const getSignificanceColor = (isSignificant: boolean) => {
    return isSignificant ? 'green' : 'orange'
  }

  return (
    <Box>
      {/* Header */}
      <HStack justify="space-between" marginBottom={6}>
        <Box>
          <Heading size="xl">{result.test_name}</Heading>
          <HStack marginTop={2}>
            <Badge colorPalette={getStatusColor(result.status)}>
              {result.status.toUpperCase()}
            </Badge>
            <Text color="gray.500">Goal: {result.goal.replace('_', ' ')}</Text>
          </HStack>
        </Box>
      </HStack>

      {/* Winner Banner */}
      {result.statistical_analysis.is_significant && (
        <Card.Root
          backgroundColor={isDark ? 'green.900' : 'green.50'}
          borderColor="green.500"
          borderWidth="2px"
          marginBottom={6}
        >
          <Card.Body>
            <HStack gap={4}>
              <Box fontSize="3xl">
                <FaTrophy color="gold" />
              </Box>
              <Box flex="1">
                <Heading size="md" color="green.600">
                  {result.conclusion.winner} Wins!
                </Heading>
                <Text color="green.700" marginTop={1}>
                  {result.conclusion.improvement_percentage.toFixed(1)}% improvement
                  with statistical significance
                </Text>
                <Text fontSize="sm" color="gray.600" marginTop={2}>
                  {result.conclusion.recommendation}
                </Text>
              </Box>
            </HStack>
          </Card.Body>
        </Card.Root>
      )}

      {/* Results Grid */}
      <Grid templateColumns={{ base: '1fr', lg: 'repeat(2, 1fr)' }} gap={6} marginBottom={6}>
        {/* Variant A */}
        <GridItem>
          <Card.Root
            borderWidth="2px"
            borderColor={
              result.conclusion.winner === 'Variant A'
                ? 'blue.500'
                : isDark
                ? 'gray.700'
                : 'gray.200'
            }
          >
            <Card.Header>
              <HStack justify="space-between">
                <Heading size="md">Variant A</Heading>
                {result.conclusion.winner === 'Variant A' && (
                  <Badge colorPalette="blue" variant="solid">
                    WINNER
                  </Badge>
                )}
              </HStack>
            </Card.Header>
            <Card.Body>
              <VStack align="stretch" gap={3}>
                <Box>
                  <Text fontSize="sm" color="gray.500">
                    Views
                  </Text>
                  <Heading size="lg">
                    {result.variant_a.views.toLocaleString()}
                  </Heading>
                </Box>
                <Box>
                  <Text fontSize="sm" color="gray.500">
                    Conversions/Engagement
                  </Text>
                  <Heading size="lg">
                    {result.variant_a.metric.toLocaleString()}
                  </Heading>
                </Box>
                <Box>
                  <Text fontSize="sm" color="gray.500">
                    Rate
                  </Text>
                  <Heading size="2xl" color="blue.500">
                    {(result.variant_a.rate * 100).toFixed(2)}%
                  </Heading>
                </Box>
              </VStack>
            </Card.Body>
          </Card.Root>
        </GridItem>

        {/* Variant B */}
        <GridItem>
          <Card.Root
            borderWidth="2px"
            borderColor={
              result.conclusion.winner === 'Variant B'
                ? 'green.500'
                : isDark
                ? 'gray.700'
                : 'gray.200'
            }
          >
            <Card.Header>
              <HStack justify="space-between">
                <Heading size="md">Variant B</Heading>
                {result.conclusion.winner === 'Variant B' && (
                  <Badge colorPalette="green" variant="solid">
                    WINNER
                  </Badge>
                )}
              </HStack>
            </Card.Header>
            <Card.Body>
              <VStack align="stretch" gap={3}>
                <Box>
                  <Text fontSize="sm" color="gray.500">
                    Views
                  </Text>
                  <Heading size="lg">
                    {result.variant_b.views.toLocaleString()}
                  </Heading>
                </Box>
                <Box>
                  <Text fontSize="sm" color="gray.500">
                    Conversions/Engagement
                  </Text>
                  <Heading size="lg">
                    {result.variant_b.metric.toLocaleString()}
                  </Heading>
                </Box>
                <Box>
                  <Text fontSize="sm" color="gray.500">
                    Rate
                  </Text>
                  <Heading size="2xl" color="green.500">
                    {(result.variant_b.rate * 100).toFixed(2)}%
                  </Heading>
                </Box>
              </VStack>
            </Card.Body>
          </Card.Root>
        </GridItem>
      </Grid>

      {/* Performance Comparison Chart */}
      <Card.Root marginBottom={6}>
        <Card.Header>
          <Heading size="md">Performance Comparison</Heading>
        </Card.Header>
        <Card.Body>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke={isDark ? '#374151' : '#E5E7EB'} />
              <XAxis
                dataKey="variant"
                stroke={isDark ? '#E5E7EB' : '#374151'}
                style={{ fontSize: '14px' }}
              />
              <YAxis
                stroke={isDark ? '#E5E7EB' : '#374151'}
                style={{ fontSize: '14px' }}
                label={{
                  value: 'Rate (%)',
                  angle: -90,
                  position: 'insideLeft'
                }}
              />
              <Tooltip
                contentStyle={{
                  backgroundColor: isDark ? '#1F2937' : '#FFFFFF',
                  border: `1px solid ${isDark ? '#374151' : '#E5E7EB'}`,
                  borderRadius: '8px'
                }}
                formatter={(value: number) => [`${value.toFixed(2)}%`, 'Rate']}
              />
              <Bar dataKey="rate" radius={[8, 8, 0, 0]}>
                {chartData.map((entry, index) => (
                  <Cell
                    key={`cell-${index}`}
                    fill={index === 0 ? '#3B82F6' : '#10B981'}
                  />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </Card.Body>
      </Card.Root>

      {/* Statistical Analysis */}
      <Card.Root>
        <Card.Header>
          <HStack>
            <FaChartLine />
            <Heading size="md">Statistical Analysis</Heading>
          </HStack>
        </Card.Header>
        <Card.Body>
          <Grid templateColumns={{ base: '1fr', md: 'repeat(2, 1fr)' }} gap={4}>
            <GridItem>
              <VStack align="stretch" gap={3}>
                <Box>
                  <Text fontSize="sm" color="gray.500">
                    Statistical Significance
                  </Text>
                  <HStack marginTop={1}>
                    <Badge
                      colorPalette={getSignificanceColor(
                        result.statistical_analysis.is_significant
                      )}
                      variant="solid"
                    >
                      {result.statistical_analysis.is_significant
                        ? 'SIGNIFICANT'
                        : 'NOT SIGNIFICANT'}
                    </Badge>
                  </HStack>
                </Box>

                <Box>
                  <Text fontSize="sm" color="gray.500">
                    P-Value
                  </Text>
                  <Text fontSize="xl" fontWeight="bold" marginTop={1}>
                    {result.statistical_analysis.p_value !== null
                      ? result.statistical_analysis.p_value.toFixed(6)
                      : 'N/A'}
                  </Text>
                  <Text fontSize="xs" color="gray.500">
                    (Threshold: {(1 - result.statistical_analysis.confidence_level).toFixed(2)})
                  </Text>
                </Box>

                <Box>
                  <Text fontSize="sm" color="gray.500">
                    Confidence Level
                  </Text>
                  <Text fontSize="xl" fontWeight="bold" marginTop={1}>
                    {(result.statistical_analysis.confidence_level * 100).toFixed(0)}%
                  </Text>
                  <Progress
                    value={result.statistical_analysis.confidence_level * 100}
                    marginTop={2}
                    colorPalette="blue"
                  />
                </Box>
              </VStack>
            </GridItem>

            <GridItem>
              <VStack align="stretch" gap={3}>
                <Box>
                  <Text fontSize="sm" color="gray.500">
                    Effect Size (Cohen's h)
                  </Text>
                  <HStack marginTop={1} align="baseline">
                    <Text fontSize="xl" fontWeight="bold">
                      {result.statistical_analysis.effect_size !== null
                        ? result.statistical_analysis.effect_size.toFixed(4)
                        : 'N/A'}
                    </Text>
                    <Badge colorPalette="purple">
                      {result.statistical_analysis.effect_interpretation}
                    </Badge>
                  </HStack>
                  <Text fontSize="xs" color="gray.500" marginTop={1}>
                    Small: 0.2 | Medium: 0.5 | Large: 0.8
                  </Text>
                </Box>

                <Box>
                  <Text fontSize="sm" color="gray.500">
                    Confidence Interval
                  </Text>
                  <Text fontSize="md" fontWeight="bold" marginTop={1}>
                    {result.statistical_analysis.confidence_interval || 'N/A'}
                  </Text>
                </Box>

                <Box>
                  <Text fontSize="sm" color="gray.500">
                    Sample Size Status
                  </Text>
                  <Badge
                    colorPalette={
                      result.conclusion.sample_size_sufficient ? 'green' : 'orange'
                    }
                    marginTop={1}
                  >
                    {result.conclusion.sample_size_sufficient
                      ? 'SUFFICIENT'
                      : 'INSUFFICIENT'}
                  </Badge>
                </Box>
              </VStack>
            </GridItem>
          </Grid>
        </Card.Body>
      </Card.Root>
    </Box>
  )
}
