import { createFileRoute } from '@tanstack/react-router'
import { useState } from 'react'
import {
  Box,
  Button,
  Container,
  Heading,
  HStack,
  VStack,
  Card,
  Badge,
  Text
} from '@chakra-ui/react'
import { ABTestWizard } from '../../components/ABTesting/ABTestWizard'
import { ABTestResults } from '../../components/ABTesting/ABTestResults'
import { FaPlus } from 'react-icons/fa'

export const Route = createFileRoute('/_layout/ab-tests')({
  component: ABTestsPage
})

function ABTestsPage() {
  const [showWizard, setShowWizard] = useState(false)
  const [selectedTest, setSelectedTest] = useState<string | null>(null)

  // Mock content variants
  const mockVariants = [
    { id: '1', platform: 'YouTube', title: 'Product Launch Video - Bold Headline' },
    { id: '2', platform: 'YouTube', title: 'Product Launch Video - Question Headline' },
    { id: '3', platform: 'Twitter', title: 'Product Tweet - Short Form' },
    { id: '4', platform: 'Twitter', title: 'Product Tweet - Long Form' }
  ]

  // Mock test result
  const mockTestResult = {
    test_id: 'test-123',
    test_name: 'YouTube Headline Test',
    status: 'completed' as const,
    goal: 'engagement_rate',
    variant_a: {
      views: 1250,
      metric: 187,
      rate: 0.1496
    },
    variant_b: {
      views: 1180,
      metric: 142,
      rate: 0.1203
    },
    statistical_analysis: {
      p_value: 0.0315,
      is_significant: true,
      confidence_level: 0.95,
      effect_size: 0.42,
      effect_interpretation: 'Medium',
      confidence_interval: '[0.1312, 0.1680]'
    },
    conclusion: {
      winner: 'Variant A',
      improvement_percentage: 23.5,
      sample_size_sufficient: true,
      recommendation: 'Deploy Variant A - statistically significant improvement detected'
    }
  }

  const handleCreateTest = async (config: any) => {
    console.log('Creating test:', config)
    // API call would go here
    await new Promise((resolve) => setTimeout(resolve, 1000))
    setShowWizard(false)
  }

  if (showWizard) {
    return (
      <Container maxWidth="container.xl" paddingY={8}>
        <ABTestWizard
          contentVariants={mockVariants}
          onSubmit={handleCreateTest}
          onCancel={() => setShowWizard(false)}
        />
      </Container>
    )
  }

  if (selectedTest) {
    return (
      <Container maxWidth="container.xl" paddingY={8}>
        <Button
          variant="ghost"
          onClick={() => setSelectedTest(null)}
          marginBottom={6}
        >
          ← Back to Tests
        </Button>
        <ABTestResults result={mockTestResult} />
      </Container>
    )
  }

  return (
    <Container maxWidth="container.xl" paddingY={8}>
      <HStack justify="space-between" marginBottom={8}>
        <Heading size="2xl">A/B Tests</Heading>
        <Button
          colorPalette="blue"
          leftIcon={<FaPlus />}
          onClick={() => setShowWizard(true)}
        >
          Create New Test
        </Button>
      </HStack>

      {/* Tests List */}
      <VStack gap={4} align="stretch">
        <Card.Root
          cursor="pointer"
          onClick={() => setSelectedTest('test-123')}
          _hover={{ shadow: 'lg' }}
        >
          <Card.Body>
            <HStack justify="space-between">
              <Box>
                <Heading size="md">YouTube Headline Test</Heading>
                <Text color="gray.500" marginTop={1}>
                  Goal: Engagement Rate
                </Text>
              </Box>
              <VStack align="end">
                <Badge colorPalette="green">COMPLETED</Badge>
                <Text fontSize="sm" color="gray.500">
                  Winner: Variant A (+23.5%)
                </Text>
              </VStack>
            </HStack>
          </Card.Body>
        </Card.Root>

        <Card.Root variant="outline" opacity={0.6}>
          <Card.Body>
            <HStack justify="space-between">
              <Box>
                <Heading size="md">Twitter CTA Test</Heading>
                <Text color="gray.500" marginTop={1}>
                  Goal: Click-Through Rate
                </Text>
              </Box>
              <Badge colorPalette="blue">RUNNING</Badge>
            </HStack>
          </Card.Body>
        </Card.Root>

        <Card.Root variant="outline" opacity={0.4}>
          <Card.Body>
            <HStack justify="space-between">
              <Box>
                <Heading size="md">Instagram Caption Test</Heading>
                <Text color="gray.500" marginTop={1}>
                  Goal: Reach
                </Text>
              </Box>
              <Badge colorPalette="gray">DRAFT</Badge>
            </HStack>
          </Card.Body>
        </Card.Root>
      </VStack>
    </Container>
  )
}
