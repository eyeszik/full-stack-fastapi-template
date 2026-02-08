import { useState } from 'react'
import {
  Box,
  Button,
  HStack,
  VStack,
  Heading,
  Text,
  Input,
  Textarea,
  Card,
  Field,
  Stepper,
  useColorMode,
  Alert
} from '@chakra-ui/react'
import { FaCheckCircle } from 'react-icons/fa'

interface ABTestConfig {
  name: string
  description: string
  goal: 'engagement_rate' | 'click_through_rate' | 'conversion_rate' | 'reach' | 'watch_time'
  confidence_level: number
  min_sample_size: number
  variant_a_id: string
  variant_b_id: string
}

interface ABTestWizardProps {
  contentVariants: Array<{ id: string; platform: string; title: string }>
  onSubmit: (config: ABTestConfig) => Promise<void>
  onCancel: () => void
}

const GOAL_OPTIONS = [
  {
    value: 'engagement_rate',
    label: 'Engagement Rate',
    description: 'Likes + Comments + Shares / Views'
  },
  {
    value: 'click_through_rate',
    label: 'Click-Through Rate',
    description: 'Clicks / Views'
  },
  {
    value: 'conversion_rate',
    label: 'Conversion Rate',
    description: 'Conversions / Views'
  },
  {
    value: 'reach',
    label: 'Reach',
    description: 'Total unique viewers'
  },
  {
    value: 'watch_time',
    label: 'Watch Time',
    description: 'Total watch time in seconds'
  }
]

export const ABTestWizard: React.FC<ABTestWizardProps> = ({
  contentVariants,
  onSubmit,
  onCancel
}) => {
  const { colorMode } = useColorMode()
  const [currentStep, setCurrentStep] = useState(0)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const [config, setConfig] = useState<ABTestConfig>({
    name: '',
    description: '',
    goal: 'engagement_rate',
    confidence_level: 0.95,
    min_sample_size: 100,
    variant_a_id: '',
    variant_b_id: ''
  })

  const steps = [
    { title: 'Basic Info', description: 'Name and description' },
    { title: 'Goal', description: 'Select success metric' },
    { title: 'Variants', description: 'Choose content to test' },
    { title: 'Settings', description: 'Configure thresholds' }
  ]

  const handleNext = () => {
    if (currentStep < steps.length - 1) {
      setCurrentStep(currentStep + 1)
    }
  }

  const handleBack = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1)
    }
  }

  const handleSubmit = async () => {
    // Validation
    if (!config.name.trim()) {
      setError('Please enter a test name')
      return
    }
    if (!config.variant_a_id || !config.variant_b_id) {
      setError('Please select both variants')
      return
    }
    if (config.variant_a_id === config.variant_b_id) {
      setError('Variants must be different')
      return
    }

    setLoading(true)
    setError(null)

    try {
      await onSubmit(config)
    } catch (err: any) {
      setError(err.message || 'Failed to create A/B test')
    } finally {
      setLoading(false)
    }
  }

  const isNextDisabled = () => {
    switch (currentStep) {
      case 0:
        return !config.name.trim()
      case 2:
        return !config.variant_a_id || !config.variant_b_id
      default:
        return false
    }
  }

  return (
    <Box maxWidth="800px" margin="0 auto">
      {/* Stepper */}
      <Stepper.Root
        value={currentStep}
        count={steps.length}
        marginBottom={8}
        colorPalette="blue"
      >
        <Stepper.List>
          {steps.map((step, index) => (
            <Stepper.Item key={index} index={index}>
              <Stepper.Trigger>
                <Stepper.Indicator>
                  {index < currentStep ? <FaCheckCircle /> : index + 1}
                </Stepper.Indicator>
                <Stepper.Title>{step.title}</Stepper.Title>
                <Stepper.Description>{step.description}</Stepper.Description>
              </Stepper.Trigger>
            </Stepper.Item>
          ))}
        </Stepper.List>
      </Stepper.Root>

      {error && (
        <Alert.Root status="error" marginBottom={4}>
          <Alert.Icon />
          <Alert.Title>{error}</Alert.Title>
        </Alert.Root>
      )}

      <Card.Root>
        <Card.Body>
          {/* Step 0: Basic Info */}
          {currentStep === 0 && (
            <VStack gap={4} align="stretch">
              <Heading size="lg">Test Information</Heading>

              <Field.Root>
                <Field.Label>Test Name</Field.Label>
                <Input
                  value={config.name}
                  onChange={(e) => setConfig({ ...config, name: e.target.value })}
                  placeholder="e.g., Headline Comparison - Product Launch"
                />
                <Field.HelpText>Give your test a descriptive name</Field.HelpText>
              </Field.Root>

              <Field.Root>
                <Field.Label>Description (Optional)</Field.Label>
                <Textarea
                  value={config.description}
                  onChange={(e) => setConfig({ ...config, description: e.target.value })}
                  placeholder="Describe what you're testing and why..."
                  rows={4}
                />
              </Field.Root>
            </VStack>
          )}

          {/* Step 1: Goal */}
          {currentStep === 1 && (
            <VStack gap={4} align="stretch">
              <Heading size="lg">Select Success Metric</Heading>
              <Text color="gray.500">
                Choose what metric you want to optimize for in this test
              </Text>

              <VStack gap={3} align="stretch">
                {GOAL_OPTIONS.map((option) => (
                  <Card.Root
                    key={option.value}
                    variant={config.goal === option.value ? 'elevated' : 'outline'}
                    cursor="pointer"
                    onClick={() =>
                      setConfig({
                        ...config,
                        goal: option.value as ABTestConfig['goal']
                      })
                    }
                    borderColor={
                      config.goal === option.value
                        ? 'blue.500'
                        : colorMode === 'dark'
                        ? 'gray.700'
                        : 'gray.200'
                    }
                    borderWidth={config.goal === option.value ? '2px' : '1px'}
                  >
                    <Card.Body>
                      <HStack justify="space-between">
                        <Box>
                          <Text fontWeight="bold">{option.label}</Text>
                          <Text fontSize="sm" color="gray.500">
                            {option.description}
                          </Text>
                        </Box>
                        {config.goal === option.value && (
                          <FaCheckCircle color="blue" size={20} />
                        )}
                      </HStack>
                    </Card.Body>
                  </Card.Root>
                ))}
              </VStack>
            </VStack>
          )}

          {/* Step 2: Variants */}
          {currentStep === 2 && (
            <VStack gap={4} align="stretch">
              <Heading size="lg">Select Content Variants</Heading>
              <Text color="gray.500">
                Choose two content variants to compare (A/B test)
              </Text>

              <Field.Root>
                <Field.Label>Variant A</Field.Label>
                <select
                  value={config.variant_a_id}
                  onChange={(e) =>
                    setConfig({ ...config, variant_a_id: e.target.value })
                  }
                  style={{
                    width: '100%',
                    padding: '8px 12px',
                    borderRadius: '6px',
                    border: `1px solid ${
                      colorMode === 'dark' ? '#4A5568' : '#E2E8F0'
                    }`,
                    backgroundColor: colorMode === 'dark' ? '#2D3748' : 'white',
                    color: colorMode === 'dark' ? 'white' : 'black'
                  }}
                >
                  <option value="">Select variant...</option>
                  {contentVariants.map((variant) => (
                    <option key={variant.id} value={variant.id}>
                      {variant.title} ({variant.platform})
                    </option>
                  ))}
                </select>
              </Field.Root>

              <Field.Root>
                <Field.Label>Variant B</Field.Label>
                <select
                  value={config.variant_b_id}
                  onChange={(e) =>
                    setConfig({ ...config, variant_b_id: e.target.value })
                  }
                  style={{
                    width: '100%',
                    padding: '8px 12px',
                    borderRadius: '6px',
                    border: `1px solid ${
                      colorMode === 'dark' ? '#4A5568' : '#E2E8F0'
                    }`,
                    backgroundColor: colorMode === 'dark' ? '#2D3748' : 'white',
                    color: colorMode === 'dark' ? 'white' : 'black'
                  }}
                >
                  <option value="">Select variant...</option>
                  {contentVariants.map((variant) => (
                    <option key={variant.id} value={variant.id}>
                      {variant.title} ({variant.platform})
                    </option>
                  ))}
                </select>
              </Field.Root>
            </VStack>
          )}

          {/* Step 3: Settings */}
          {currentStep === 3 && (
            <VStack gap={4} align="stretch">
              <Heading size="lg">Test Configuration</Heading>
              <Text color="gray.500">
                Set statistical thresholds for your test
              </Text>

              <Field.Root>
                <Field.Label>Confidence Level</Field.Label>
                <Input
                  type="number"
                  min={0.8}
                  max={0.99}
                  step={0.01}
                  value={config.confidence_level}
                  onChange={(e) =>
                    setConfig({
                      ...config,
                      confidence_level: parseFloat(e.target.value)
                    })
                  }
                />
                <Field.HelpText>
                  Default: 0.95 (95% confidence). Higher = more certainty required
                </Field.HelpText>
              </Field.Root>

              <Field.Root>
                <Field.Label>Minimum Sample Size</Field.Label>
                <Input
                  type="number"
                  min={30}
                  step={10}
                  value={config.min_sample_size}
                  onChange={(e) =>
                    setConfig({
                      ...config,
                      min_sample_size: parseInt(e.target.value)
                    })
                  }
                />
                <Field.HelpText>
                  Minimum views/impressions before declaring a winner
                </Field.HelpText>
              </Field.Root>

              {/* Summary */}
              <Card.Root variant="subtle" marginTop={4}>
                <Card.Header>
                  <Heading size="sm">Test Summary</Heading>
                </Card.Header>
                <Card.Body>
                  <VStack align="stretch" gap={2}>
                    <HStack justify="space-between">
                      <Text fontSize="sm" color="gray.500">
                        Name:
                      </Text>
                      <Text fontSize="sm" fontWeight="bold">
                        {config.name}
                      </Text>
                    </HStack>
                    <HStack justify="space-between">
                      <Text fontSize="sm" color="gray.500">
                        Goal:
                      </Text>
                      <Text fontSize="sm" fontWeight="bold">
                        {
                          GOAL_OPTIONS.find((g) => g.value === config.goal)
                            ?.label
                        }
                      </Text>
                    </HStack>
                    <HStack justify="space-between">
                      <Text fontSize="sm" color="gray.500">
                        Confidence:
                      </Text>
                      <Text fontSize="sm" fontWeight="bold">
                        {(config.confidence_level * 100).toFixed(0)}%
                      </Text>
                    </HStack>
                    <HStack justify="space-between">
                      <Text fontSize="sm" color="gray.500">
                        Min Sample:
                      </Text>
                      <Text fontSize="sm" fontWeight="bold">
                        {config.min_sample_size}
                      </Text>
                    </HStack>
                  </VStack>
                </Card.Body>
              </Card.Root>
            </VStack>
          )}
        </Card.Body>

        <Card.Footer>
          <HStack justify="space-between" width="100%">
            <Button
              variant="ghost"
              onClick={currentStep === 0 ? onCancel : handleBack}
            >
              {currentStep === 0 ? 'Cancel' : 'Back'}
            </Button>

            <HStack>
              {currentStep < steps.length - 1 ? (
                <Button
                  colorPalette="blue"
                  onClick={handleNext}
                  disabled={isNextDisabled()}
                >
                  Next
                </Button>
              ) : (
                <Button
                  colorPalette="blue"
                  onClick={handleSubmit}
                  loading={loading}
                >
                  Create Test
                </Button>
              )}
            </HStack>
          </HStack>
        </Card.Footer>
      </Card.Root>
    </Box>
  )
}
