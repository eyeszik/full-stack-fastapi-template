import { useState } from 'react'
import {
  Box,
  Button,
  HStack,
  VStack,
  Heading,
  Text,
  Card,
  Stepper,
  Alert,
  Code,
  Input,
  Field,
  useColorMode
} from '@chakra-ui/react'
import {
  FaYoutube,
  FaTwitter,
  FaInstagram,
  FaFacebook,
  FaLinkedin,
  FaTiktok,
  FaMedium,
  FaCheckCircle,
  FaExternalLinkAlt
} from 'react-icons/fa'

interface Platform {
  id: string
  name: string
  icon: any
  color: string
  authUrl: string
  docsUrl: string
  scopes: string[]
}

const PLATFORMS: Platform[] = [
  {
    id: 'youtube',
    name: 'YouTube',
    icon: FaYoutube,
    color: '#FF0000',
    authUrl: 'https://console.cloud.google.com/apis/credentials',
    docsUrl: 'https://developers.google.com/youtube/v3/getting-started',
    scopes: [
      'https://www.googleapis.com/auth/youtube.upload',
      'https://www.googleapis.com/auth/youtube.readonly'
    ]
  },
  {
    id: 'twitter',
    name: 'Twitter/X',
    icon: FaTwitter,
    color: '#1DA1F2',
    authUrl: 'https://developer.twitter.com/en/portal/dashboard',
    docsUrl: 'https://developer.twitter.com/en/docs/authentication/oauth-2-0',
    scopes: ['tweet.read', 'tweet.write', 'users.read']
  },
  {
    id: 'instagram',
    name: 'Instagram',
    icon: FaInstagram,
    color: '#E4405F',
    authUrl: 'https://developers.facebook.com/apps/',
    docsUrl: 'https://developers.facebook.com/docs/instagram-basic-display-api',
    scopes: ['user_profile', 'user_media', 'instagram_content_publish']
  },
  {
    id: 'facebook',
    name: 'Facebook',
    icon: FaFacebook,
    color: '#1877F2',
    authUrl: 'https://developers.facebook.com/apps/',
    docsUrl: 'https://developers.facebook.com/docs/facebook-login',
    scopes: ['pages_manage_posts', 'pages_read_engagement', 'pages_manage_metadata']
  },
  {
    id: 'linkedin',
    name: 'LinkedIn',
    icon: FaLinkedin,
    color: '#0A66C2',
    authUrl: 'https://www.linkedin.com/developers/apps',
    docsUrl: 'https://docs.microsoft.com/en-us/linkedin/',
    scopes: ['w_member_social', 'r_basicprofile', 'r_organization_social']
  },
  {
    id: 'tiktok',
    name: 'TikTok',
    icon: FaTiktok,
    color: '#000000',
    authUrl: 'https://developers.tiktok.com/apps/',
    docsUrl: 'https://developers.tiktok.com/doc/overview',
    scopes: ['video.upload', 'user.info.basic']
  }
]

interface OAuthWizardProps {
  onComplete: (credentials: {
    platform: string
    accessToken: string
    refreshToken?: string
    expiresAt?: string
  }) => Promise<void>
  onCancel: () => void
}

export const OAuthWizard: React.FC<OAuthWizardProps> = ({ onComplete, onCancel }) => {
  const { colorMode } = useColorMode()
  const [currentStep, setCurrentStep] = useState(0)
  const [selectedPlatform, setSelectedPlatform] = useState<Platform | null>(null)
  const [accessToken, setAccessToken] = useState('')
  const [refreshToken, setRefreshToken] = useState('')
  const [expiresAt, setExpiresAt] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const steps = [
    { title: 'Select Platform', description: 'Choose social media platform' },
    { title: 'Get Credentials', description: 'Obtain OAuth credentials' },
    { title: 'Configure', description: 'Enter access tokens' },
    { title: 'Verify', description: 'Test connection' }
  ]

  const handlePlatformSelect = (platform: Platform) => {
    setSelectedPlatform(platform)
    setCurrentStep(1)
  }

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
    if (!selectedPlatform || !accessToken) {
      setError('Access token is required')
      return
    }

    setLoading(true)
    setError(null)

    try {
      await onComplete({
        platform: selectedPlatform.id,
        accessToken,
        refreshToken: refreshToken || undefined,
        expiresAt: expiresAt || undefined
      })
    } catch (err: any) {
      setError(err.message || 'Failed to connect account')
    } finally {
      setLoading(false)
    }
  }

  return (
    <Box maxWidth="900px" margin="0 auto">
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

      {/* Step 0: Select Platform */}
      {currentStep === 0 && (
        <Box>
          <Heading size="lg" marginBottom={4}>
            Select Platform to Connect
          </Heading>
          <Grid templateColumns={{ base: '1fr', md: 'repeat(2, 1fr)', lg: 'repeat(3, 1fr)' }} gap={4}>
            {PLATFORMS.map((platform) => {
              const Icon = platform.icon
              return (
                <Card.Root
                  key={platform.id}
                  cursor="pointer"
                  onClick={() => handlePlatformSelect(platform)}
                  _hover={{
                    transform: 'translateY(-4px)',
                    shadow: 'lg',
                    borderColor: platform.color
                  }}
                  transition="all 0.2s"
                  borderWidth="2px"
                  borderColor={
                    selectedPlatform?.id === platform.id
                      ? platform.color
                      : 'transparent'
                  }
                >
                  <Card.Body>
                    <VStack gap={3}>
                      <Box fontSize="3xl" color={platform.color}>
                        <Icon />
                      </Box>
                      <Heading size="md">{platform.name}</Heading>
                    </VStack>
                  </Card.Body>
                </Card.Root>
              )
            })}
          </Grid>
        </Box>
      )}

      {/* Step 1: Get Credentials */}
      {currentStep === 1 && selectedPlatform && (
        <Card.Root>
          <Card.Header>
            <HStack>
              <Box fontSize="2xl" color={selectedPlatform.color}>
                {<selectedPlatform.icon />}
              </Box>
              <Heading size="lg">Get {selectedPlatform.name} API Credentials</Heading>
            </HStack>
          </Card.Header>
          <Card.Body>
            <VStack align="stretch" gap={4}>
              <Alert.Root status="info">
                <Alert.Icon />
                <Alert.Description>
                  Follow these steps to obtain your OAuth credentials from{' '}
                  {selectedPlatform.name}.
                </Alert.Description>
              </Alert.Root>

              <Box>
                <Heading size="sm" marginBottom={2}>
                  Step 1: Create Developer Application
                </Heading>
                <Text marginBottom={2}>
                  Visit the {selectedPlatform.name} Developer Portal and create a new
                  application:
                </Text>
                <Button
                  as="a"
                  href={selectedPlatform.authUrl}
                  target="_blank"
                  rel="noopener noreferrer"
                  colorPalette="blue"
                  rightIcon={<FaExternalLinkAlt />}
                >
                  Open Developer Portal
                </Button>
              </Box>

              <Box>
                <Heading size="sm" marginBottom={2}>
                  Step 2: Configure OAuth Scopes
                </Heading>
                <Text marginBottom={2}>Request the following permissions/scopes:</Text>
                <VStack align="stretch" gap={1}>
                  {selectedPlatform.scopes.map((scope, index) => (
                    <Code key={index} padding={2}>
                      {scope}
                    </Code>
                  ))}
                </VStack>
              </Box>

              <Box>
                <Heading size="sm" marginBottom={2}>
                  Step 3: Set Redirect URI
                </Heading>
                <Text marginBottom={2}>
                  Configure your application's redirect URI to:
                </Text>
                <Code padding={2} display="block">
                  {window.location.origin}/api/v1/oauth/callback
                </Code>
              </Box>

              <Box>
                <Heading size="sm" marginBottom={2}>
                  Step 4: Documentation
                </Heading>
                <Button
                  as="a"
                  href={selectedPlatform.docsUrl}
                  target="_blank"
                  rel="noopener noreferrer"
                  variant="outline"
                  rightIcon={<FaExternalLinkAlt />}
                >
                  View {selectedPlatform.name} Documentation
                </Button>
              </Box>
            </VStack>
          </Card.Body>
          <Card.Footer>
            <HStack justify="space-between" width="100%">
              <Button variant="ghost" onClick={handleBack}>
                Back
              </Button>
              <Button colorPalette="blue" onClick={handleNext}>
                I've Created the App
              </Button>
            </HStack>
          </Card.Footer>
        </Card.Root>
      )}

      {/* Step 2: Configure Tokens */}
      {currentStep === 2 && selectedPlatform && (
        <Card.Root>
          <Card.Header>
            <Heading size="lg">Enter OAuth Credentials</Heading>
          </Card.Header>
          <Card.Body>
            <VStack align="stretch" gap={4}>
              <Alert.Root status="warning">
                <Alert.Icon />
                <Alert.Description>
                  Keep your tokens secure. Never share them publicly or commit them to
                  version control.
                </Alert.Description>
              </Alert.Root>

              <Field.Root required>
                <Field.Label>Access Token</Field.Label>
                <Input
                  type="password"
                  value={accessToken}
                  onChange={(e) => setAccessToken(e.target.value)}
                  placeholder="Enter your access token..."
                />
                <Field.HelpText>
                  Copy the access token from your {selectedPlatform.name} app dashboard
                </Field.HelpText>
              </Field.Root>

              <Field.Root>
                <Field.Label>Refresh Token (Optional)</Field.Label>
                <Input
                  type="password"
                  value={refreshToken}
                  onChange={(e) => setRefreshToken(e.target.value)}
                  placeholder="Enter refresh token if available..."
                />
                <Field.HelpText>
                  Used to automatically renew expired access tokens
                </Field.HelpText>
              </Field.Root>

              <Field.Root>
                <Field.Label>Token Expiration (Optional)</Field.Label>
                <Input
                  type="datetime-local"
                  value={expiresAt}
                  onChange={(e) => setExpiresAt(e.target.value)}
                />
                <Field.HelpText>When does this token expire?</Field.HelpText>
              </Field.Root>
            </VStack>
          </Card.Body>
          <Card.Footer>
            <HStack justify="space-between" width="100%">
              <Button variant="ghost" onClick={handleBack}>
                Back
              </Button>
              <Button
                colorPalette="blue"
                onClick={handleSubmit}
                loading={loading}
                disabled={!accessToken}
              >
                Connect Account
              </Button>
            </HStack>
          </Card.Footer>
        </Card.Root>
      )}

      {/* Step 3: Verify (shown after successful connection) */}
      {currentStep === 3 && selectedPlatform && (
        <Card.Root>
          <Card.Body>
            <VStack gap={4}>
              <Box fontSize="5xl" color="green.500">
                <FaCheckCircle />
              </Box>
              <Heading size="lg">
                {selectedPlatform.name} Account Connected!
              </Heading>
              <Text color="gray.500">
                Your account has been successfully connected. You can now schedule and
                publish content to {selectedPlatform.name}.
              </Text>
              <Button colorPalette="blue" onClick={onCancel}>
                Done
              </Button>
            </VStack>
          </Card.Body>
        </Card.Root>
      )}
    </Box>
  )
}

// Missing import for Grid
import { Grid } from '@chakra-ui/react'
