import { createFileRoute } from '@tanstack/react-router'
import { useState } from 'react'
import {
  Box,
  Button,
  Container,
  Grid,
  Heading,
  HStack,
  VStack,
  Card,
  Badge,
  Text,
  IconButton
} from '@chakra-ui/react'
import { OAuthWizard } from '../../components/SocialAccounts/OAuthWizard'
import {
  FaYoutube,
  FaTwitter,
  FaInstagram,
  FaFacebook,
  FaLinkedin,
  FaTiktok,
  FaPlus,
  FaTrash,
  FaCheckCircle
} from 'react-icons/fa'

export const Route = createFileRoute('/_layout/social-accounts')({
  component: SocialAccountsPage
})

interface SocialAccount {
  id: string
  platform: string
  account_name: string
  account_handle: string
  is_active: boolean
  token_expires_at: string | null
}

const PLATFORM_ICONS: Record<string, any> = {
  youtube: FaYoutube,
  twitter: FaTwitter,
  instagram: FaInstagram,
  facebook: FaFacebook,
  linkedin: FaLinkedin,
  tiktok: FaTiktok
}

const PLATFORM_COLORS: Record<string, string> = {
  youtube: 'red.500',
  twitter: 'blue.400',
  instagram: 'pink.500',
  facebook: 'blue.600',
  linkedin: 'blue.700',
  tiktok: 'gray.900'
}

function SocialAccountsPage() {
  const [showWizard, setShowWizard] = useState(false)

  // Mock connected accounts
  const [accounts, setAccounts] = useState<SocialAccount[]>([
    {
      id: '1',
      platform: 'youtube',
      account_name: 'My Channel',
      account_handle: '@mychannel',
      is_active: true,
      token_expires_at: '2026-03-01T00:00:00Z'
    },
    {
      id: '2',
      platform: 'twitter',
      account_name: 'My Twitter',
      account_handle: '@mytwitter',
      is_active: true,
      token_expires_at: null
    }
  ])

  const handleConnect = async (credentials: any) => {
    console.log('Connecting account:', credentials)
    // API call would go here
    await new Promise((resolve) => setTimeout(resolve, 1000))

    // Add mock account
    const newAccount: SocialAccount = {
      id: Date.now().toString(),
      platform: credentials.platform,
      account_name: `${credentials.platform} Account`,
      account_handle: `@${credentials.platform}`,
      is_active: true,
      token_expires_at: credentials.expiresAt || null
    }

    setAccounts([...accounts, newAccount])
    setShowWizard(false)
  }

  const handleDisconnect = async (accountId: string) => {
    if (confirm('Are you sure you want to disconnect this account?')) {
      setAccounts(accounts.filter((a) => a.id !== accountId))
    }
  }

  if (showWizard) {
    return (
      <Container maxWidth="container.xl" paddingY={8}>
        <OAuthWizard
          onComplete={handleConnect}
          onCancel={() => setShowWizard(false)}
        />
      </Container>
    )
  }

  return (
    <Container maxWidth="container.xl" paddingY={8}>
      <HStack justify="space-between" marginBottom={8}>
        <Box>
          <Heading size="2xl">Social Accounts</Heading>
          <Text color="gray.500" marginTop={2}>
            Connect your social media accounts to start publishing content
          </Text>
        </Box>
        <Button
          colorPalette="blue"
          leftIcon={<FaPlus />}
          onClick={() => setShowWizard(true)}
        >
          Connect Account
        </Button>
      </HStack>

      {accounts.length === 0 ? (
        <Card.Root>
          <Card.Body>
            <VStack paddingY={12} gap={4}>
              <Text fontSize="lg" color="gray.500">
                No accounts connected yet
              </Text>
              <Button
                colorPalette="blue"
                leftIcon={<FaPlus />}
                onClick={() => setShowWizard(true)}
              >
                Connect Your First Account
              </Button>
            </VStack>
          </Card.Body>
        </Card.Root>
      ) : (
        <Grid templateColumns={{ base: '1fr', md: 'repeat(2, 1fr)' }} gap={4}>
          {accounts.map((account) => {
            const Icon = PLATFORM_ICONS[account.platform]
            const color = PLATFORM_COLORS[account.platform]
            const isExpiring =
              account.token_expires_at &&
              new Date(account.token_expires_at) < new Date(Date.now() + 7 * 24 * 60 * 60 * 1000)

            return (
              <Card.Root key={account.id}>
                <Card.Body>
                  <HStack justify="space-between" marginBottom={4}>
                    <HStack>
                      <Box fontSize="2xl" color={color}>
                        {Icon && <Icon />}
                      </Box>
                      <Box>
                        <Heading size="md">{account.account_name}</Heading>
                        <Text fontSize="sm" color="gray.500">
                          {account.account_handle}
                        </Text>
                      </Box>
                    </HStack>
                    <HStack>
                      {account.is_active && (
                        <Box color="green.500">
                          <FaCheckCircle />
                        </Box>
                      )}
                      <IconButton
                        aria-label="Disconnect account"
                        size="sm"
                        variant="ghost"
                        colorPalette="red"
                        onClick={() => handleDisconnect(account.id)}
                      >
                        <FaTrash />
                      </IconButton>
                    </HStack>
                  </HStack>

                  <VStack align="stretch" gap={2}>
                    <HStack justify="space-between">
                      <Text fontSize="sm" color="gray.500">
                        Platform:
                      </Text>
                      <Badge>
                        {account.platform.charAt(0).toUpperCase() +
                          account.platform.slice(1)}
                      </Badge>
                    </HStack>

                    <HStack justify="space-between">
                      <Text fontSize="sm" color="gray.500">
                        Status:
                      </Text>
                      <Badge colorPalette={account.is_active ? 'green' : 'red'}>
                        {account.is_active ? 'Active' : 'Inactive'}
                      </Badge>
                    </HStack>

                    {account.token_expires_at && (
                      <HStack justify="space-between">
                        <Text fontSize="sm" color="gray.500">
                          Token Expires:
                        </Text>
                        <Text
                          fontSize="sm"
                          color={isExpiring ? 'orange.500' : 'gray.600'}
                        >
                          {new Date(account.token_expires_at).toLocaleDateString()}
                        </Text>
                      </HStack>
                    )}

                    {isExpiring && (
                      <Badge colorPalette="orange" marginTop={2}>
                        Token expiring soon
                      </Badge>
                    )}
                  </VStack>
                </Card.Body>
              </Card.Root>
            )
          })}
        </Grid>
      )}
    </Container>
  )
}
